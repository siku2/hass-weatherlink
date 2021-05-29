import dataclasses
import logging
from typing import Any, Dict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import config_validation as cv

from .api import WeatherLinkSession
from .const import DOMAIN
from .units import UnitConfig, get_unit_config

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
        return OptionsFlow(config_entry)

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
    config_entry: config_entries.ConfigEntry
    options: dict
    units_config: dict

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        super().__init__()
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        return await self.async_step_misc()

    async def async_step_misc(self, user_input=None):
        from . import get_update_interval

        errors = {}
        if user_input is not None:
            try:
                self.options["update_interval"] = cv.time_period_str(
                    user_input["update_interval"]
                ).total_seconds()
            except vol.Error:
                errors["update_interval"] = "invalid_time_period"
            else:
                return await self.async_step_units()

        return self.async_show_form(
            step_id="misc",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "update_interval",
                        default=str(get_update_interval(self.config_entry)),
                    ): str
                }
            ),
            errors=errors,
        )

    async def async_step_units(self, user_input=None):
        if user_input is not None:
            self.units_config = user_input
            return await self.async_step_rounding()

        return self.async_show_form(
            step_id="units",
            data_schema=get_unit_config(self.hass, self.config_entry).units_schema(),
        )

    async def async_step_rounding(self, user_input=None):
        if user_input is not None:
            config = UnitConfig.from_config_flow(self.units_config, user_input)
            self.options["units"] = config.as_dict()
            return await self.finish()

        return self.async_show_form(
            step_id="rounding",
            data_schema=get_unit_config(self.hass, self.config_entry).rounding_schema(),
        )

    async def finish(self):
        return self.async_create_entry(title="", data=self.options)
