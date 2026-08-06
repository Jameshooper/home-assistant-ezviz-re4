"""Cached, explicitly refreshed robot-camera image."""

from __future__ import annotations

from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EzvizRs20ProCoordinator


async def async_setup_entry(
    hass: Any,
    entry: ConfigEntry[EzvizRs20ProCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the cached snapshot image."""
    async_add_entities([EzvizRs20ProCameraImage(hass, entry.runtime_data)])


class EzvizRs20ProCameraImage(
    CoordinatorEntity[EzvizRs20ProCoordinator], ImageEntity
):
    """Last image captured after an explicit service call."""

    _attr_has_entity_name = True
    _attr_translation_key = "camera_snapshot"
    _attr_content_type = "image/jpeg"

    def __init__(self, hass: Any, coordinator: EzvizRs20ProCoordinator) -> None:
        ImageEntity.__init__(self, hass)
        CoordinatorEntity.__init__(self, coordinator)
        serial = coordinator.data["serial"]
        self._attr_unique_id = f"{serial}_camera_snapshot"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="EZVIZ",
            model="RS20 Pro",
            name="EZVIZ RS20 Pro",
        )

    @property
    def image_last_updated(self):
        """Return when the user last requested a snapshot."""
        return self.coordinator.camera_snapshot_updated

    async def async_image(self) -> bytes | None:
        """Return the cached image without opening the robot camera."""
        return self.coordinator.camera_snapshot
