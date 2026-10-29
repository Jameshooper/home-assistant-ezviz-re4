"""RE4 requests layered on the authenticated pyezviz client."""

from __future__ import annotations

import base64
import gzip
from importlib import metadata
import json
from typing import Any
import zlib


class EzvizRe4ApiError(Exception):
    """Raised when the RE4 endpoint rejects a request."""


class EzvizRe4Api:
    """Use the official integration's session without copying credentials."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def query_current_task(self, serial: str) -> dict[str, Any]:
        """Query current task; this action does not move or configure the robot."""
        return self._iot_request(
            serial,
            endpoint="action",
            domain="SweeperTaskMgr",
            identifier="QueryCurrentTask",
            payload={},
        )

    def clean_control(self, serial: str, command: str) -> dict[str, Any]:
        """Run one of the documented cleaning controls."""
        if command not in {"start", "pause", "stop", "return_charge"}:
            raise ValueError(f"Nieobsługiwana komenda RE4: {command}")
        return self._iot_request(
            serial,
            endpoint="action",
            domain="SweeperCleanTask",
            identifier="CleanControl",
            payload=command,
        )

    def start_region_clean(
        self,
        serial: str,
        *,
        map_id: int,
        rooms: list[dict[str, Any]],
        clean_mode: str = "sweep",
    ) -> dict[str, Any]:
        """Start cleaning selected map rooms using the robot's native action."""
        if not rooms:
            raise ValueError("Nie wybrano żadnego pomieszczenia")
        payload = {
            "cleanMode": clean_mode,
            "mapID": int(map_id),
            "region": rooms,
            "edgeDeepClean": False,
        }
        return self._iot_request(
            serial,
            endpoint="action",
            domain="SweeperCleanTask",
            identifier="StartRegionClean",
            payload=payload,
        )

    def client_diagnostics(self) -> dict[str, Any]:
        """Return non-secret client capability and service-host information."""
        token = getattr(self._client, "_token", None)
        service_urls: dict[str, Any] = {}
        if isinstance(token, dict) and isinstance(token.get("service_urls"), dict):
            service_urls = token["service_urls"]
        version = "unknown"
        try:
            version = metadata.version("pyezvizapi")
        except metadata.PackageNotFoundError:
            pass
        return {
            "pyezvizapi_version": version,
            "client_module": type(self._client).__module__,
            "capabilities": {
                name: hasattr(self._client, name)
                for name in (
                    "_api_get_pagelist",
                    "_http_request",
                    "_parse_json",
                    "_request_json",
                    "get_cam_key",
                    "get_service_urls",
                )
            },
            "service_urls": service_urls,
        }

    def query_map_path_candidates(self, serial: str, map_id: int) -> list[dict[str, Any]]:
        """Probe known read-only map-path routes used by EZVIZ applications."""
        session = getattr(self._client, "_session", None)
        token = getattr(self._client, "_token", None)
        if session is None or not isinstance(token, dict):
            raise EzvizRe4ApiError("Aktywna sesja EZVIZ jest niedostępna")
        api_url = token.get("api_url")
        if not api_url:
            raise EzvizRe4ApiError("Brak adresu API w aktywnej sesji EZVIZ")

        routes = (
            "/v3/specialBizs/sweeprobot/v3/rule/path",
            "/api/specialbiz/v3/sweeprobot/v3/rule/path",
        )
        payload = {"deviceSerial": serial.upper(), "mapId": str(map_id)}
        results: list[dict[str, Any]] = []
        for route in routes:
            try:
                response = session.post(
                    f"https://{api_url}{route}",
                    data=payload,
                    timeout=getattr(self._client, "_timeout", 25),
                )
                parsed: Any
                try:
                    parsed = response.json()
                except ValueError:
                    parsed = {"response_type": response.headers.get("Content-Type", "")}
                results.append(
                    {
                        "route": route,
                        "http_status": response.status_code,
                        "response": parsed,
                    }
                )
            except Exception as err:
                results.append({"route": route, "error": str(err)})
        return results

    @staticmethod
    def decode_diagnostic_blob(blob: Any) -> Any:
        """Decode the gzip/base64 diagnostic fields reported by the robot."""
        if not isinstance(blob, dict) or not isinstance(blob.get("content"), str):
            return None
        try:
            raw = base64.b64decode(blob["content"], validate=True)
        except (ValueError, TypeError):
            return {"error": "Nieprawidłowe kodowanie base64"}

        decoded: bytes | None = None
        for decoder in (
            gzip.decompress,
            zlib.decompress,
            lambda data: zlib.decompress(data, -zlib.MAX_WBITS),
        ):
            try:
                decoded = decoder(raw)
                break
            except (OSError, zlib.error):
                continue
        if decoded is None:
            decoded = raw
        try:
            text = decoded.decode("utf-8")
        except UnicodeDecodeError:
            return {"binary_bytes": len(decoded)}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"text": text[:4000], "truncated": len(text) > 4000}

    def _iot_request(
        self,
        serial: str,
        *,
        endpoint: str,
        domain: str,
        identifier: str,
        payload: Any,
    ) -> dict[str, Any]:
        session = getattr(self._client, "_session", None)
        token = getattr(self._client, "_token", None)
        if session is None or not isinstance(token, dict):
            raise EzvizRe4ApiError("Aktywna sesja EZVIZ jest niedostępna")
        api_url = token.get("api_url")
        if not api_url:
            raise EzvizRe4ApiError("Brak adresu API w aktywnej sesji EZVIZ")

        url = (
            f"https://{api_url}/v3/iot-feature/{endpoint}/"
            f"{serial.upper()}/SweepingRobot/0/{domain}/{identifier}"
        )
        headers = dict(session.headers)
        headers["Content-Type"] = "application/json"
        response = session.put(
            url,
            headers=headers,
            data=json.dumps(payload, separators=(",", ":")),
            timeout=getattr(self._client, "_timeout", 25),
        )
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict):
            raise EzvizRe4ApiError("EZVIZ zwrócił nieprawidłową odpowiedź")

        meta = result.get("meta")
        code = meta.get("code") if isinstance(meta, dict) else result.get("code")
        if code not in (None, 0, 200, "0", "200"):
            message = meta.get("message") if isinstance(meta, dict) else result.get("msg")
            raise EzvizRe4ApiError(f"EZVIZ odrzucił żądanie {code}: {message}")
        return result
