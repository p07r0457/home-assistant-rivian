"""Rivian (Unofficial)"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback


from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_COORDINATOR,
    DOMAIN,
    NAME,
    SENSORS,
)

from .data_classes import RivianSensorEntity

from . import (
    get_device_identifier,
    RivianEntity,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the sensor entities"""
    coordinator = hass.data[DOMAIN][entry.entry_id][ATTR_COORDINATOR]

    entities = []
    for _, value in enumerate(SENSORS):
        entities.append(
            RivianSensor(
                coordinator=coordinator,
                config_entry=entry,
                sensor=SENSORS[value],
                prop_key=value,
            )
        )
    async_add_entities(entities, True)


class RivianSensor(RivianEntity, CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(
        self,
        coordinator,
        config_entry,
        sensor: RivianSensorEntity,
        prop_key: str,
    ):
        """"""
        CoordinatorEntity.__init__(self, coordinator)
        SensorEntity.__init__(self)
        super().__init__(coordinator)
        self._sensor = sensor
        self.entity_description = sensor.entity_description
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._name = self.entity_description.key
        self._prop_key = prop_key
        self.entity_id = f"sensor.{self.entity_description.key}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{DOMAIN}_{self._name}_{self._config_entry.entry_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Get device information."""
        return {
            "identifiers": {get_device_identifier(self._config_entry)},
            "name": NAME,
            "manufacturer": NAME,
        }

    @property
    def native_value(self) -> str:
        try:
            entity = self.coordinator.data[self._prop_key]
            if self._sensor.value_lambda is None:
                return entity[1]
            else:
                return self._sensor.value_lambda(entity[1])
        except KeyError:
            return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        try:
            entity = self.coordinator.data[self._prop_key]
            return {
                "last_update": entity[0],
            }
        except KeyError:
            return None
