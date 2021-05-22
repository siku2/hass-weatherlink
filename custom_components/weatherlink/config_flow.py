import dataclasses
import logging
from typing import Any, Dict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import aiohttp_client

from .api import WeatherLinkSession
from .const import DOMAIN

logger = logging.getLogger(__name__)

FORM_SCHEMA = vol.Schema({vol.Required("host"): str})


@dataclasses.dataclass()
class FormError(Exception):
    key: str
    message: str


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return OptionsFlow()

    async def discover(self, host: str) -> dict:
        logger.info("discovering: %s", host)

        session = aiohttp_client.async_get_clientsession(self.hass)
        session = WeatherLinkSession(session, host)
        try:
            conditions = await session.current_conditions()
        except Exception:
            logger.exception(f"failed to connect to {host!r}")
            raise FormError("host", "connect_failed")

        await self.async_set_unique_id(conditions.did)
        self._abort_if_unique_id_configured()

        title = conditions.determine_device_name()
        return self.async_create_entry(title=title, data={"host": host})

    async def async_step_user(self, info):
        errors = {}
        if info is not None:
            host: str = info["host"].rstrip("/")
            if not host.startswith(("http://", "https://")):
                host = f"http://{host}"

            try:
                return await self.discover(host)
            except FormError as e:
                errors[e.key] = e.message

        return self.async_show_form(
            step_id="user", data_schema=FORM_SCHEMA, errors=errors
        )

    async def async_step_zeroconf(
        self, discovery_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        host: str = discovery_info["host"]
        port: int = discovery_info["port"]
        try:
            self.discovery_data = await self.discover(f"http://{host}:{port}")
            return await self.async_step_zeroconf_confirm()
        except FormError as e:
            return self.async_abort(reason=e.message)

    async def async_step_zeroconf_confirm(self, user_input=None):
        if user_input is not None:
            self.discovery_data["title"] = user_input["title"]
            return self.discovery_data

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema(
                {vol.Optional("title", default=self.discovery_data["title"]): str}
            ),
        )


class OptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "show_things",
                        default=self.config_entry.options.get("show_things"),
                    ): bool
                }
            ),
        )
