import logging

from homeassistant.helpers.entity import Entity

from .const import DOMAIN

from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS
)

_LOGGER = logging.getLogger(__name__)

PROTECT_SENSOR_TYPES = [
    "co_status",
    "smoke_status",
    "battery_health_state"
]


async def async_setup_platform(hass,
                               config,
                               async_add_entities,
                               discovery_info=None):
    """Set up the Nest climate device."""
    api = hass.data[DOMAIN]['api']

    temperature_sensors = []
    _LOGGER.info("Adding temperature sensors")
    for sensor in api['temperature_sensors']:
        _LOGGER.info(f"Adding nest temp sensor uuid: {sensor}")
        temperature_sensors.append(NestTemperatureSensor(sensor, api))

    async_add_entities(temperature_sensors)

    protect_sensors = []
    _LOGGER.info("Adding protect sensors")
    for sensor in api['protects']:
        _LOGGER.info(f"Adding nest protect sensor uuid: {sensor}")
        for sensor_type in PROTECT_SENSOR_TYPES:
            protect_sensors.append(NestProtectSensor(sensor, sensor_type, api))

    async_add_entities(protect_sensors)

    camera_event_sensors = []
    _LOGGER.info("Adding nest camera event sensors")
    for sensor in api["cameras"]:
        _LOGGER.info(f"Adding nest camera event sensor uuid: {sensor}")
        for sensor_type in PROTECT_SENSOR_TYPES:
            camera_event_sensors.append(NestCameraEventSensor(sensor, api))

    async_add_entities(camera_event_sensors)


class NestTemperatureSensor(Entity):
    """Implementation of the Nest Temperature Sensor."""

    def __init__(self, device_id, api):
        """Initialize the sensor."""
        self._name = "Nest Temperature Sensor"
        self._unit_of_measurement = TEMP_CELSIUS
        self.device_id = device_id
        self.device = api

    @property
    def unique_id(self):
        """Return an unique ID."""
        return self.device_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.device.device_data[self.device_id]['name']

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.device.device_data[self.device_id]['temperature']

    @property
    def device_class(self):
        """Return the device class of this entity."""
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def update(self):
        """Get the latest data from the DHT and updates the states."""
        self.device.update()

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_BATTERY_LEVEL:
                self.device.device_data[self.device_id]['battery_level']
        }


class NestProtectSensor(Entity):
    """Implementation of the Nest Protect sensor."""

    def __init__(self, device_id, sensor_type, api):
        """Initialize the sensor."""
        self._name = "Nest Protect Sensor"
        self.device_id = device_id
        self._sensor_type = sensor_type
        self.device = api

    @property
    def unique_id(self):
        """Return an unique ID."""
        return self.device_id + '_' + self._sensor_type

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.device.device_data[self.device_id]['name'] + \
            f' {self._sensor_type}'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.device.device_data[self.device_id][self._sensor_type]

    def update(self):
        """Get the latest data from the Protect and updates the states."""
        self.device.update()


class NestCameraEventSensor(Entity):
    """Implementation of Nest Camera Event Sensor"""

    def __init__(self, device_id, api):
        """Initialize the sensor."""
        self._name = "Nest Event Sensor"
        self.device_id = device_id
        self.device = api

    @property
    def unique_id(self):
        """Return an unique ID."""
        return self.device_id

    @property
    def state(self):
        """Return the state of the sensor."""
        try:
            return self.device.device_data[self.device_id]["events"][0]["start_time"]
        except (IndexError, TypeError):
            return None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.device.device_data[self.device_id]["name"] + " Events"

    @property
    def device_state_attributes(self):
        return {"Events": self.device.device_data[self.device_id]["events"]}

    def update(self):
        """Get the latest data from the Protect and updates the states."""
        self.device.update()
