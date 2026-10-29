"""Sensors for EZVIZ RE4."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfArea
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EzvizRe4ProCoordinator


@dataclass(frozen=True, kw_only=True)
class Re4SensorDescription(SensorEntityDescription):
    """Describe a value in the RE4 response."""

    source_key: str
    remaining_percent: bool = False


SENSORS: Final = (
    Re4SensorDescription(
        key="battery",
        translation_key="battery",
        source_key="SurplusPower",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    Re4SensorDescription(
        key="total_clean_area",
        translation_key="total_clean_area",
        source_key="totalCleanArea",
        native_unit_of_measurement=UnitOfArea.SQUARE_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:texture-box",
    ),
    Re4SensorDescription(
        key="main_brush",
        translation_key="main_brush",
        source_key="RotatingBrushWorkingTime",
        remaining_percent=True,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:brush",
    ),
    Re4SensorDescription(
        key="side_brush",
        translation_key="side_brush",
        source_key="EdgeBrushWorkingTime",
        remaining_percent=True,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:brush-outline",
    ),
    Re4SensorDescription(
        key="hepa_filter",
        translation_key="hepa_filter",
        source_key="HepaWorkingTime",
        remaining_percent=True,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
    ),
    Re4SensorDescription(
        key="mop",
        translation_key="mop",
        source_key="MopWorkingTime",
        remaining_percent=True,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water",
    ),
    Re4SensorDescription(
        key="sensors",
        translation_key="sensors",
        source_key="SensorWorkingTime",
        remaining_percent=True,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radar",
    ),
)


def _find_mapping(value: Any, key: str) -> Mapping[str, Any] | None:
    """Find a named mapping in a nested response."""
    if isinstance(value, Mapping):
        for current_key, item in value.items():
            if str(current_key).casefold() == key.casefold() and isinstance(item, Mapping):
                return item
        for item in value.values():
            found = _find_mapping(item, key)
            if found is not None:
                return found
    elif isinstance(value, (list, tuple)):
        for item in value:
            found = _find_mapping(item, key)
            if found is not None:
                return found
    return None


def _find_scalar(value: Any, key: str) -> Any | None:
    """Find a named scalar in a nested response."""
    if isinstance(value, Mapping):
        for current_key, item in value.items():
            if str(current_key).casefold() == key.casefold() and not isinstance(item, (Mapping, list, tuple)):
                return item
        for item in value.values():
            found = _find_scalar(item, key)
            if found is not None:
                return found
    elif isinstance(value, (list, tuple)):
        for item in value:
            found = _find_scalar(item, key)
            if found is not None:
                return found
    return None


async def async_setup_entry(
    hass: Any,
    entry: ConfigEntry[EzvizRe4ProCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RE4 sensors."""
    async_add_entities(
        Re4Sensor(entry.runtime_data, description) for description in SENSORS
    )


class Re4Sensor(CoordinatorEntity[EzvizRe4ProCoordinator], SensorEntity):
    """A sensor sourced from the RE4 feature report."""

    _attr_has_entity_name = True
    entity_description: Re4SensorDescription

    def __init__(
        self,
        coordinator: EzvizRe4ProCoordinator,
        description: Re4SensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        serial = coordinator.data["serial"]
        self._attr_unique_id = f"{serial}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="EZVIZ",
            model="RE4",
            name="EZVIZ RE4",
        )

    @property
    def native_value(self) -> int | float | str | None:
        """Return the current value."""
        device = self.coordinator.data["device"]
        if self.entity_description.remaining_percent:
            block = _find_mapping(device, self.entity_description.source_key)
            if block is None:
                return None
            try:
                rest = float(block["rest"])
                used = float(block["used"])
            except (KeyError, TypeError, ValueError):
                return None
            total = rest + used
            return round(rest * 100 / total) if total > 0 else 0

        raw = _find_scalar(device, self.entity_description.source_key)
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return None
        return int(value) if value.is_integer() else value
