# EZVIZ RE4 for Home Assistant

[Polski](README.pl.md) · English

An unofficial Home Assistant custom integration for the **EZVIZ RE4**
robot vacuum. Tested with model `CS-RE4C-YWT`.

> This project is experimental and uses cloud endpoints observed in the EZVIZ
> app because EZVIZ does not publish an API for the robot. Firmware or cloud
> changes may temporarily break individual features.

## Features

- Start, pause, stop and return the robot to the dock.
- Native room selection and room cleaning in Home Assistant.
- Battery and consumable-life sensors (main brush, side brush, HEPA filter,
  mop pads, sensors).
- Sanitized protocol and map diagnostics.
- UI translations: English, Polish, German, French, Spanish and Italian.

## Requirements

- Home Assistant 2026.7 or newer.
- An EZVIZ RE4 already added to the EZVIZ mobile app.
- The official **EZVIZ** Home Assistant integration configured and loaded.
- Internet access from Home Assistant to the EZVIZ cloud.

The custom integration reuses the official integration's authenticated session.
It does not ask for or store another copy of your EZVIZ username or password.

## Install with HACS

1. Open HACS in Home Assistant.
2. Open **Integrations**, then the three-dot menu and **Custom repositories**.
3. Add `https://github.com/Jameshooper/home-assistant-ezviz-rs20-pro` as an
   **Integration** repository.
4. Find **EZVIZ RE4**, select **Download**, then restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and choose
   **EZVIZ RE4**.
6. Select the official EZVIZ account entry. Leave the serial number empty for
   automatic discovery, or enter it when the account has several robots.

## Manual installation

1. Download the source archive from the latest GitHub release.
2. Copy `custom_components/ezviz_rs20pro` into Home Assistant's
   `/config/custom_components/` directory.
3. Restart Home Assistant and add **EZVIZ RE4** from the integration UI.

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
