"""Multi-step GUI config flow for Couch Control."""
from __future__ import annotations
import logging
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    AreaSelector, AreaSelectorConfig, DeviceSelector, DeviceSelectorConfig,
    EntitySelector, EntitySelectorConfig,
)
from .const import CONF_AREAS, CONF_DEVICES, CONF_ENTITIES, DOMAIN
from .storage import async_load_entities, async_save_entities
_LOGGER = logging.getLogger(__name__)
FLOW_BUILD = "1.3.0-beta.4"
_LOGGER.info("Loaded Couch Control GUI config flow %s", FLOW_BUILD)

def _valid_entities(hass, values: list[str]) -> list[str]:
    registry = er.async_get(hass)
    return [eid for eid in values if eid in registry.entities or hass.states.get(eid)]

class _SelectionMixin:
    _areas: list[str]
    _devices: list[str]
    _entities: list[str]

    async def _save(self) -> None:
        data = {CONF_AREAS: self._areas, CONF_DEVICES: self._devices, CONF_ENTITIES: self._entities}
        await async_save_entities(self.hass, data)
        if DOMAIN in self.hass.data:
            from . import _resolve_filter
            resolved = _resolve_filter(self.hass, areas=self._areas, devices=self._devices, entities=self._entities)
            self.hass.data[DOMAIN]["entities"] = sorted(resolved)
            self.hass.data[DOMAIN]["areas"] = self._areas
            self.hass.data[DOMAIN]["devices"] = self._devices

class CouchControlConfigFlow(_SelectionMixin, config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    def __init__(self) -> None:
        self._areas, self._devices, self._entities = [], [], []

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            self._areas = list(user_input.get(CONF_AREAS, []))
            return await self.async_step_devices()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Optional(CONF_AREAS, default=[]): AreaSelector(AreaSelectorConfig(multiple=True))}
            ),
        )

    async def async_step_devices(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self._devices = list(user_input.get(CONF_DEVICES, []))
            return await self.async_step_entities()
        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {vol.Optional(CONF_DEVICES, default=[]): DeviceSelector(DeviceSelectorConfig(multiple=True))}
            ),
        )

    async def async_step_entities(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self._entities = _valid_entities(self.hass, list(user_input.get(CONF_ENTITIES, [])))
            await self._save()
            return self.async_create_entry(title="Couch Control Entity Filter", data={CONF_AREAS:self._areas, CONF_DEVICES:self._devices, CONF_ENTITIES:self._entities})
        return self.async_show_form(
            step_id="entities",
            data_schema=vol.Schema(
                {vol.Optional(CONF_ENTITIES, default=[]): EntitySelector(EntitySelectorConfig(multiple=True))}
            ),
            description_placeholders={
                "area_count": str(len(self._areas)),
                "device_count": str(len(self._devices)),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CouchControlOptionsFlow()

class CouchControlOptionsFlow(_SelectionMixin, config_entries.OptionsFlow):
    def __init__(self) -> None:
        self._areas, self._devices, self._entities = [], [], []
        self._loaded = False

    async def _load(self):
        if not self._loaded:
            current = await async_load_entities(self.hass)
            self._areas = list(current.get(CONF_AREAS, self.config_entry.data.get(CONF_AREAS, [])))
            self._devices = list(current.get(CONF_DEVICES, self.config_entry.data.get(CONF_DEVICES, [])))
            self._entities = list(current.get(CONF_ENTITIES, self.config_entry.data.get(CONF_ENTITIES, [])))
            self._loaded = True

    async def async_step_init(self, user_input=None):
        await self._load()
        if user_input is not None:
            self._areas = list(user_input.get(CONF_AREAS, []))
            return await self.async_step_devices()
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Optional(CONF_AREAS, default=self._areas): AreaSelector(AreaSelectorConfig(multiple=True))}
            ),
        )

    async def async_step_devices(self, user_input=None):
        if user_input is not None:
            self._devices = list(user_input.get(CONF_DEVICES, []))
            return await self.async_step_entities()
        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {vol.Optional(CONF_DEVICES, default=self._devices): DeviceSelector(DeviceSelectorConfig(multiple=True))}
            ),
        )

    async def async_step_entities(self, user_input=None):
        if user_input is not None:
            self._entities = _valid_entities(self.hass, list(user_input.get(CONF_ENTITIES, [])))
            await self._save()
            return self.async_create_entry(title="", data={CONF_AREAS:self._areas, CONF_DEVICES:self._devices, CONF_ENTITIES:self._entities})
        return self.async_show_form(
            step_id="entities",
            data_schema=vol.Schema(
                {vol.Optional(CONF_ENTITIES, default=self._entities): EntitySelector(EntitySelectorConfig(multiple=True))}
            ),
            description_placeholders={
                "area_count": str(len(self._areas)),
                "device_count": str(len(self._devices)),
            },
        )
