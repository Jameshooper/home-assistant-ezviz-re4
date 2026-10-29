"""Coordinator for EZVIZ RE4."""

from __future__ import annotations

from collections.abc import Mapping
from functools import partial
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import EzvizRe4Api
from .const import (
    CONF_SERIAL,
    CONF_SOURCE_ENTRY_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


def _find_api(runtime_data: Any) -> Any | None:
    """Find the pyezviz client without depending on HA's private data class."""
    candidates = (
        runtime_data,
        getattr(runtime_data, "coordinator", None),
        getattr(runtime_data, "data", None),
    )
    for candidate in candidates:
        if candidate is None:
            continue
        for attribute in ("api", "client", "ezviz_client"):
            api = getattr(candidate, attribute, None)
            if api is not None and hasattr(api, "get_device_infos"):
                return api
        if hasattr(candidate, "get_device_infos"):
            return candidate
    return None


def _is_sweeping_robot(value: Any) -> bool:
    """Return whether a nested response identifies a EZVIZ sweeping robot."""
    if isinstance(value, str):
        normalized = value.casefold().replace("-", "").replace(" ", "")
        return "sweepingrobot" in normalized
    if isinstance(value, Mapping):
        return any(_is_sweeping_robot(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_is_sweeping_robot(item) for item in value)
    return False


class EzvizRe4Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch RE4 data through the already authenticated EZVIZ client."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        source_entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.entry = entry
        self.source_entry = source_entry
        self.serial: str = entry.data.get(CONF_SERIAL, "")
        self.re4_api: EzvizRe4Api | None = None

    def _api(self) -> Any:
        if self.source_entry.state is not ConfigEntryState.LOADED:
            raise ConfigEntryNotReady("Oficjalna integracja EZVIZ nie jest załadowana")
        api = _find_api(getattr(self.source_entry, "runtime_data", None))
        if api is None:
            raise ConfigEntryNotReady("Nie znaleziono aktywnej sesji EZVIZ")
        return api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            source_api = self._api()
            raw = await self.hass.async_add_executor_job(source_api.get_device_infos)
        except ConfigEntryNotReady:
            raise
        except Exception as err:
            raise UpdateFailed(f"Błąd odczytu EZVIZ: {err}") from err

        if not isinstance(raw, Mapping):
            raise UpdateFailed("EZVIZ zwrócił nieprawidłowy zestaw urządzeń")

        selected_serial = self.serial
        if selected_serial:
            selected = raw.get(selected_serial)
            if not isinstance(selected, Mapping):
                raise UpdateFailed(f"Nie znaleziono urządzenia {selected_serial}")
        else:
            matches = [
                (str(serial), payload)
                for serial, payload in raw.items()
                if isinstance(payload, Mapping) and _is_sweeping_robot(payload)
            ]
            if not matches:
                raise UpdateFailed("Nie znaleziono EZVIZ RE4 na koncie")
            selected_serial, selected = matches[0]
            self.serial = selected_serial

        self.re4_api = EzvizRe4Api(source_api)
        task: dict[str, Any] = {}
        task_error: str | None = None
        try:
            task = await self.hass.async_add_executor_job(
                self.re4_api.query_current_task,
                selected_serial,
            )
        except Exception as err:
            task_error = str(err)

        return {
            "serial": selected_serial,
            "device": dict(selected),
            "task": task,
            "task_error": task_error,
        }

    async def async_clean_control(self, command: str) -> None:
        """Send a documented robot control and refresh state."""
        if self.re4_api is None:
            raise UpdateFailed("Klient RE4 nie jest gotowy")
        await self.hass.async_add_executor_job(
            self.re4_api.clean_control,
            self.serial,
            command,
        )
        await self.async_request_refresh()

    async def async_recharge(self) -> None:
        """Send the robot back to its base and refresh state."""
        if self.re4_api is None:
            raise UpdateFailed("RE4 client is not ready")
        await self.hass.async_add_executor_job(
            self.re4_api.recharge_control,
            self.serial,
            "start",
        )
        await self.async_request_refresh()

    def active_map_rooms(self) -> tuple[int, list[int]]:
        """Return the in-use map ID and its room IDs from the robot's config."""
        try:
            map_mgr = self.data["device"]["FEATURE_INFO"]["0"]["SweepingRobot"][
                "SweeperMapMgr"
            ]
            maps = map_mgr["MapBasicProperty"]
            active = next((item for item in maps if item.get("inUse")), maps[0])
            map_id = int(active["mapID"])
            configs = next(
                item["room"]
                for item in map_mgr["RoomCustomCleanCfg"]
                if int(item["mapID"]) == map_id
            )
            return map_id, [int(room["roomID"]) for room in configs]
        except (KeyError, IndexError, StopIteration, TypeError, ValueError) as err:
            raise UpdateFailed("No room configuration reported for the RE4") from err

    async def async_clean_segments(self, segment_ids: list[str]) -> None:
        """Start a native room-cleaning task on the in-use map."""
        if self.re4_api is None:
            raise UpdateFailed("RE4 client is not ready")
        map_id, known = self.active_map_rooms()
        try:
            room_ids = [int(item) for item in segment_ids]
        except ValueError as err:
            raise UpdateFailed("Invalid RE4 room selection") from err
        missing = sorted(set(room_ids) - set(known))
        if missing:
            raise UpdateFailed(f"Unknown RE4 rooms: {', '.join(map(str, missing))}")
        await self.hass.async_add_executor_job(
            partial(
                self.re4_api.start_region_clean,
                self.serial,
                map_id=map_id,
                room_ids=room_ids,
            )
        )
        await self.async_request_refresh()


def get_source_entry(hass: HomeAssistant, entry: ConfigEntry) -> ConfigEntry:
    """Resolve the official EZVIZ config entry."""
    source_id = entry.data[CONF_SOURCE_ENTRY_ID]
    source = hass.config_entries.async_get_entry(source_id)
    if source is None:
        raise ConfigEntryNotReady("Brak wskazanej integracji EZVIZ")
    return source
