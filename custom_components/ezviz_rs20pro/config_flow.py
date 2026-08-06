"""Config flow for EZVIZ RS20 Pro."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import CONF_SERIAL, CONF_SOURCE_ENTRY_ID, DOMAIN, SOURCE_DOMAIN


class EzvizRs20ProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure EZVIZ RS20 Pro by reusing the official EZVIZ session."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        source_entries = self.hass.config_entries.async_entries(SOURCE_DOMAIN)
        if not source_entries:
            return self.async_abort(reason="ezviz_not_configured")

        if user_input is not None:
            source_entry_id = user_input[CONF_SOURCE_ENTRY_ID]
            serial = user_input.get(CONF_SERIAL, "").strip().upper()
            source = next(
                (entry for entry in source_entries if entry.entry_id == source_entry_id),
                None,
            )
            if source is None:
                return self.async_abort(reason="ezviz_not_configured")

            return self.async_create_entry(
                title="EZVIZ RS20 Pro",
                data={
                    CONF_SOURCE_ENTRY_ID: source_entry_id,
                    CONF_SERIAL: serial,
                },
            )

        options = [
            selector.SelectOptionDict(value=entry.entry_id, label=entry.title)
            for entry in source_entries
        ]
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SOURCE_ENTRY_ID,
                    default=source_entries[0].entry_id,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_SERIAL, default=""): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
