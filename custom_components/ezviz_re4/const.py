"""Constants for the EZVIZ RE4 integration."""

from datetime import timedelta

DOMAIN = "ezviz_re4"
SOURCE_DOMAIN = "ezviz"

CONF_SOURCE_ENTRY_ID = "source_entry_id"
CONF_SERIAL = "serial"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

SERVICE_INSPECT = "inspect"
SERVICE_MAP_DIAGNOSTICS = "map_diagnostics"
SERVICE_CAMERA_DIAGNOSTICS = "camera_diagnostics"
SERVICE_REFRESH_CAMERA = "refresh_camera_snapshot"
