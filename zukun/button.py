"""Support for IP Cameras."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

_LOGGER = logging.getLogger('ZukunButton')


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a generic IP Camera."""
    async_add_entities(
        [GenericButton(hass, entry.options, "Record"),
         GenericButton(hass, entry.options, "Turn Off"),
         ]
    )

class GenericButton(ButtonEntity):
    """Representation of a Button."""

    def __init__(
        self,
        hass: HomeAssistant,
        options: Mapping[str, Any],

        name: str,
    ) -> None:
        """Initialize button entity."""
        _LOGGER.info("Initializing button entity")
        _LOGGER.info("Button options: %s", options)
        self._attr_name = f"{name} Button"
        self._hass = hass
        self._options = options


    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Button pressed")
        # Implement the action to be performed when the button is pressed
        await asyncio.sleep(1)  # Simulate a delay for the action
        _LOGGER.info("Button action completed")
