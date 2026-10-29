"""EZVIZ RE4 integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse

from .const import (
    DOMAIN,
    SERVICE_INSPECT,
    SERVICE_MAP_DIAGNOSTICS,
)
from .coordinator import EzvizRe4Coordinator, get_source_entry

PLATFORMS = [Platform.SENSOR, Platform.VACUUM]

type EzvizRe4ConfigEntry = ConfigEntry[EzvizRe4Coordinator]

_SENSITIVE_PARTS = (
    "accesscode",
    "authcode",
    "content",
    "encryptpwd",
    "key",
    "password",
    "pwd",
    "secret",
    "session",
    "token",
    "verificationcode",
)


def _sanitize(value: Any) -> Any:
    """Remove authentication material while preserving protocol metadata."""
    if isinstance(value, Mapping):
        return {
            str(key): "[redacted]"
            if any(part in str(key).casefold() for part in _SENSITIVE_PARTS)
            else _sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    return value


async def async_setup_entry(
    hass: HomeAssistant, entry: EzvizRe4ConfigEntry
) -> bool:
    """Set up EZVIZ RE4 from a config entry."""
    coordinator = EzvizRe4Coordinator(hass, entry, get_source_entry(hass, entry))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_INSPECT):

        async def async_inspect(call: ServiceCall) -> dict[str, Any]:
            """Return sanitized raw device data for protocol discovery."""
            entries = hass.config_entries.async_entries(DOMAIN)
            if not entries:
                return {"error": "Integracja EZVIZ RE4 nie jest skonfigurowana"}
            active = entries[0]
            runtime = getattr(active, "runtime_data", None)
            if not isinstance(runtime, EzvizRe4Coordinator):
                return {"error": "Integracja EZVIZ RE4 nie jest załadowana"}
            await runtime.async_request_refresh()
            return _sanitize(runtime.data)

        hass.services.async_register(
            DOMAIN,
            SERVICE_INSPECT,
            async_inspect,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_MAP_DIAGNOSTICS):

        async def async_map_diagnostics(call: ServiceCall) -> dict[str, Any]:
            """Probe read-only map routes without returning authentication data."""
            entries = hass.config_entries.async_entries(DOMAIN)
            if not entries:
                return {"error": "Integracja EZVIZ RE4 nie jest skonfigurowana"}
            runtime = getattr(entries[0], "runtime_data", None)
            if not isinstance(runtime, EzvizRe4Coordinator):
                return {"error": "Integracja EZVIZ RE4 nie jest załadowana"}
            if runtime.re4_api is None:
                await runtime.async_request_refresh()
            if runtime.re4_api is None:
                return {"error": "Klient RE4 nie jest gotowy"}
            map_id = 5
            device = runtime.data.get("device", {})
            try:
                maps = device["FEATURE_INFO"]["0"]["SweepingRobot"]["SweeperMapMgr"]["MapBasicProperty"]
                if maps:
                    map_id = int(maps[0]["mapID"])
            except (KeyError, IndexError, TypeError, ValueError):
                pass
            result = await hass.async_add_executor_job(
                runtime.re4_api.query_map_path_candidates,
                runtime.serial,
                map_id,
            )
            device = runtime.data.get("device", {})
            operation = {}
            try:
                operation = device["FEATURE_INFO"]["0"]["SweepingRobot"][
                    "OperationDiagnosis"
                ]["DeviceOperationParams"]
            except (KeyError, TypeError):
                pass
            return _sanitize(
                {
                    "map_id": map_id,
                    "candidates": result,
                    "client": runtime.re4_api.client_diagnostics(),
                    "clean_history": runtime.re4_api.decode_diagnostic_blob(
                        operation.get("cleanHistory")
                    ),
                    "abnormal_history": runtime.re4_api.decode_diagnostic_blob(
                        operation.get("abnormalHistory")
                    ),
                }
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_MAP_DIAGNOSTICS,
            async_map_diagnostics,
            supports_response=SupportsResponse.ONLY,
        )

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: EzvizRe4ConfigEntry
) -> bool:
    """Unload EZVIZ RE4."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded and len(hass.config_entries.async_entries(DOMAIN)) <= 1:
        hass.services.async_remove(DOMAIN, SERVICE_INSPECT)
        hass.services.async_remove(DOMAIN, SERVICE_MAP_DIAGNOSTICS)
    return unloaded
