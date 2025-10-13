"""Sensor module for fetching device info from Zukun API."""
from collections.abc import Callable, Coroutine, Mapping
from dataclasses import dataclass
import hashlib
import logging
from typing import Any

import aiohttp

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import DOMAIN

_LOGGER = logging.getLogger("ZukunSensor")


@dataclass(frozen=True, kw_only=True)
class ZukunSensorDescription(SensorEntityDescription):
    """Describes Zukun sensor entity."""

    value_fn: Callable[..., Coroutine[Any, Any, int | float]] | None = None
    endpoint: str
    api_key: str

    async def _call_api(self, url: str) -> Any:
        """Call the API endpoint and return parsed JSON."""
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def __call__(self, client: Any) -> Any:
        """Fetch and parse value from API endpoint."""
        if self.value_fn is not None:
            return await self.value_fn(client)

        url = f"http://127.0.0.1:5000/{self.endpoint}"
        data = await self._call_api(url)
        return data.get(self.api_key)


SENSORS: tuple[ZukunSensorDescription, ...] = (
    ZukunSensorDescription(
        key="battery",
        translation_key="battery",
        native_unit_of_measurement=PERCENTAGE,
        endpoint="battery",
        api_key="battery_percent",
    ),
    ZukunSensorDescription(
        key="storage_available",
        translation_key="storage_available",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        endpoint="storage",
        api_key="free_gb",
    ),
    ZukunSensorDescription(
        key="storage_total",
        translation_key="storage_total",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        endpoint="storage",
        api_key="total_gb",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for the Zukun component."""
    sensors = [ZukunSensor(entry.options, description) for description in SENSORS]
    async_add_entities(sensors)


class ZukunSensor(SensorEntity):
    """Defines a Zukun sensor."""

    entity_description: ZukunSensorDescription

    def __init__(
        self,
        options: Mapping[str, Any],
        description: ZukunSensorDescription,
    ) -> None:
        """Initialize Zukun sensor."""
        _LOGGER.debug("Initializing Zukun sensor: %s", description.key)
        _LOGGER.debug("Sensor options: %s", options)
        _LOGGER.warning(
            "Unique ID for sensor %s: %s", description.key, self._attr_unique_id
        )
        self.entity_description = description
        url_hash = hashlib.md5(options["still_image_url"].encode()).hexdigest()
        self._attr_unique_id = f"{DOMAIN}_SENSOR_{url_hash}_{description.key}"
        _LOGGER.warning("Unique ID for sensor AFTER: %s", self._attr_unique_id)

    async def async_update(self) -> None:
        """Update Zukun sensor entity."""
        value = await self.entity_description(None)
        self._attr_native_value = value
        if isinstance(value, float):
            self._attr_native_value = f"{value:.2f}"
        self._attr_available = True
