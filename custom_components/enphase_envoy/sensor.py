"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Enphase Envoy sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        # Power sensors
        EnvoySensor(
            coordinator,
            "current_power",
            "Current Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        EnvoySensor(
            coordinator,
            "current_power_production",
            "Current Power Production",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        # Energy sensors
        EnvoySensor(
            coordinator,
            "today_energy",
            "Today Energy",
            UnitOfEnergy.WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EnvoySensor(
            coordinator,
            "week_energy",
            "Week Energy",
            UnitOfEnergy.WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EnvoySensor(
            coordinator,
            "lifetime_energy",
            "Lifetime Energy",
            UnitOfEnergy.WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EnvoySensor(
            coordinator,
            "lifetime_energy_production",
            "Lifetime Energy Production",
            UnitOfEnergy.WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        # System info sensors
        EnvoySensor(
            coordinator,
            "inverters_online",
            "Inverters Online",
            None,
            None,
            None,
        ),
        EnvoySensor(
            coordinator,
            "inverters_total",
            "Inverters Total",
            None,
            None,
            None,
        ),
        EnvoySensor(
            coordinator,
            "software_version",
            "Software Version",
            None,
            None,
            None,
        ),
        EnvoySensor(
            coordinator,
            "database_size",
            "Database Size",
            None,
            None,
            None,
        ),
        EnvoySensor(
            coordinator,
            "ip_address",
            "IP Address",
            None,
            None,
            None,
        ),
        EnvoySensor(
            coordinator,
            "microinverters_status",
            "Microinverters Status",
            None,
            None,
            None,
        ),
        EnvoySensor(
            coordinator,
            "web_status",
            "Web Status",
            None,
            None,
            None,
        ),
        EnvoySensor(
            coordinator,
            "system_live_since",
            "System Live Since",
            None,
            None,
            None,
        ),
    ]

    async_add_entities(sensors)


class EnvoySensor(CoordinatorEntity, SensorEntity):
    """Representation of an Envoy sensor."""

    def __init__(
        self,
        coordinator,
        data_key: str,
        name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = f"Enphase Envoy {name}"
        self._attr_unique_id = f"{coordinator.host}_{data_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._data_key)
