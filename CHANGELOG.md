# Changelog

## 0.6.1

- Fix start, pause, stop and return to dock on the RE4: it uses `CleanCtrl` and
  `RechargeCtrl` with an object payload, not the RS20's bare-string
  `CleanControl` (EZVIZ answered HTTP 400).
- Send room cleaning as the app does (map ID plus room IDs only).
- List rooms from the in-use map's room config, since the RE4 does not report
  `RegionBasicInfo`.
- Request formats were checked against the open-source
  [ha-ezviz-vacuum](https://github.com/stefanelul2000/ha-ezviz-vacuum) project
  (Apache-2.0), which supports RE4 models.

## 0.6.0

- Adapt the integration to the EZVIZ RE4 (`CS-RE4C-YWT`) robot vacuum.
- Remove the dock-only sensors, base-station switches and camera snapshot
  entity, which the RE4 does not report, along with the camera transport code
  (`vtm_stream`, `cloud_camera`), its services and the unused `set_clean_mode`
  and station-feature requests. The `ffmpeg` dependency and `pycryptodome`
  requirement are gone.
- Discover the robot by its `SweepingRobot` category instead of the RS20 model.
- Rename the integration domain to `ezviz_re4` and the folder to
  `custom_components/ezviz_re4`. Remove the old "EZVIZ RS20 Pro" entry and add
  "EZVIZ RE4" again after updating.

## 0.5.1

- Add an original repository-local brand icon for HACS.
- Sort manifest keys according to Home Assistant validation requirements.

## 0.5.0

- Add base-station status sensors for mop washing, mop drying, dust collection,
  water-tank draining and the optional plumbing module.
- Add safe station setting switches for child lock, automatic dust collection,
  automatic cleaning-solution dosing and rotating-brush self-cleaning.
- Add English, Polish, German, French, Spanish and Italian translations.
- Add HACS packaging, documentation, tests and GitHub validation workflows.
- Keep the robot camera privacy-first: snapshots are captured only on request.

## 0.4.2

- Add native room cleaning, on-demand camera snapshots, maintenance sensors and
  diagnostics for the RS20 Pro cloud protocol.
