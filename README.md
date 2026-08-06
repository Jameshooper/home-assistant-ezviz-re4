# EZVIZ RS20 Pro for Home Assistant

[Polski](README.pl.md) · English

An unofficial Home Assistant custom integration for the **EZVIZ RS20 Pro**
robot vacuum and its base station. Tested with model `CS-RS20-PRO-PGA2`.

> This project is experimental and uses cloud endpoints observed in the EZVIZ
> app because EZVIZ does not publish an API for the robot. Firmware or cloud
> changes may temporarily break individual features.

## Features

- Start, pause, stop and return the robot to the dock.
- Native room selection and room cleaning in Home Assistant.
- Battery, cleaned area and consumable-life sensors.
- Base-station status: mop washing, mop drying, dust collection, tank draining
  and optional water inlet/outlet module detection.
- Base-station settings: child lock, automatic dust collection, automatic
  cleaning-solution dosing and rotating-brush self-cleaning.
- Privacy-first robot-camera snapshot, captured only after an explicit action.
- Sanitized protocol, map and camera diagnostics.
- UI translations: English, Polish, German, French, Spanish and Italian.

Manual station actions that directly start the heater, pump or dust motor are
not exposed until their protocol is verified. The setting switches above use
confirmed feature identifiers and do not run a maintenance cycle when the
integration starts.

## Requirements

- Home Assistant 2026.7 or newer.
- An EZVIZ RS20 Pro already added to the EZVIZ mobile app.
- The official **EZVIZ** Home Assistant integration configured and loaded.
- Internet access from Home Assistant to the EZVIZ cloud.

The custom integration reuses the official integration's authenticated session.
It does not ask for or store another copy of your EZVIZ username or password.

## Install with HACS

1. Open HACS in Home Assistant.
2. Open **Integrations**, then the three-dot menu and **Custom repositories**.
3. Add `https://github.com/Dmgerr/home-assistant-ezviz-rs20-pro` as an
   **Integration** repository.
4. Find **EZVIZ RS20 Pro**, select **Download**, then restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and choose
   **EZVIZ RS20 Pro**.
6. Select the official EZVIZ account entry. Leave the serial number empty for
   automatic discovery, or enter it when the account has several robots.

## Manual installation

1. Download the source archive from the latest GitHub release.
2. Copy `custom_components/ezviz_rs20pro` into Home Assistant's
   `/config/custom_components/` directory.
3. Restart Home Assistant and add **EZVIZ RS20 Pro** from the integration UI.

## Camera privacy

The image entity contains only the latest in-memory snapshot. The camera stream
opens for a few seconds only when `ezviz_rs20pro.refresh_camera_snapshot` is
called and closes immediately afterwards. The integration does not continuously
record, write snapshots to disk or automatically open the camera.

## Troubleshooting

- If setup says that EZVIZ is missing, configure or reload the official EZVIZ
  integration first.
- After upgrading, restart Home Assistant so new platforms and translations are
  loaded.
- If a cloud action stops working after an EZVIZ update, open an issue with the
  Home Assistant version, robot firmware, model and sanitized diagnostics. Never
  post credentials, session IDs, verification codes or unredacted logs.

## Development

Run the request-adapter tests with:

```bash
python -m unittest discover -s tests -v
```

HACS validation, Hassfest and the unit tests run automatically on GitHub.

## License and disclaimer

Licensed under Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
This project is unofficial and is not affiliated with or endorsed by EZVIZ.
Use it at your own risk.
