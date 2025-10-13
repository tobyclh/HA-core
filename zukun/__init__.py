"""The generic component."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

DOMAIN = "zukun"
PLATFORMS = [Platform.BUTTON, Platform.CAMERA, Platform.SENSOR]
_LOGGER = logging.getLogger('ZukunInit')

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def _async_migrate_unique_ids(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Migrate entity unique_ids from old format to new format."""


    @callback
    def _async_migrator(entity_entry: er.RegistryEntry) -> dict[str, Any] | None:
        old_unique_id = entity_entry.unique_id

        # Skip if it already follows the correct pattern (DOMAIN_...something...)
        if old_unique_id.startswith(f"{DOMAIN}_"):
            return None

        # Otherwise, treat this as legacy: migrate based on entity_id name
        # Extract the tail of entity_id after domain, e.g. sensor.zukun_xxx_battery -> xxx_battery
        entity_suffix = entity_entry.entity_id.split(f"{DOMAIN}_")[-1]
        new_unique_id = f"{DOMAIN}_{entity_suffix}"

        # If somehow this new_unique_id already exists, skip migration
        ent_reg = er.async_get(hass)
        if ent_reg.async_get_entity_id(entity_entry.domain, DOMAIN, new_unique_id) or ent_reg.async_get_entity_id(entity_entry.domain, DOMAIN, entity_entry.previous_unique_id):
            return None

        return {"new_unique_id": new_unique_id}

    await er.async_migrate_entries(hass, entry.entry_id, _async_migrator)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up generic IP camera from a config entry."""

    await _async_migrate_unique_ids(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
