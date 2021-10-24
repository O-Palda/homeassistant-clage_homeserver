"""Platform for clage_homeserver sensor integration."""
import logging
from homeassistant.const import (
    TEMP_CELSIUS,
    ENERGY_KILO_WATT_HOUR
)

from homeassistant import core, config_entries
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    DEVICE_CLASS_ENERGY,
    SensorEntity
)


from .const import CONF_CHARGERS, DOMAIN, CONF_NAME

AMPERE = 'A'
VOLT = 'V'
POWER_KILO_WATT = 'kW'
CARD_ID = 'Card ID'
PERCENT = '%'

_LOGGER = logging.getLogger(__name__)

_sensorUnits = {
    'charger_temp': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp'},
    'charger_temp0': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp 0'},
    'charger_temp1': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp 1'},
    'charger_temp2': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp 2'},
    'charger_temp3': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp 3'},
    'p_l1': {'unit': POWER_KILO_WATT, 'name': 'Power L1'},
    'p_l2': {'unit': POWER_KILO_WATT, 'name': 'Power L2'},
    'p_l3': {'unit': POWER_KILO_WATT, 'name': 'Power L3'},
    'p_n': {'unit': POWER_KILO_WATT, 'name': 'Power N'},
    'p_all': {'unit': POWER_KILO_WATT, 'name': 'Power All'},
    'current_session_charged_energy': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Current Session charged'},
    'energy_total': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Total Charged'},
    'charge_limit': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Charge limit'},
    'u_l1': {'unit': VOLT, 'name': 'Voltage L1'},
    'u_l2': {'unit': VOLT, 'name': 'Voltage L2'},
    'u_l3': {'unit': VOLT, 'name': 'Voltage L3'},
    'u_n': {'unit': VOLT, 'name': 'Voltage N'},
    'i_l1': {'unit': AMPERE, 'name': 'Current L1'},
    'i_l2': {'unit': AMPERE, 'name': 'Current L2'},
    'i_l3': {'unit': AMPERE, 'name': 'Current L3'},
    'charger_max_current': {'unit': AMPERE, 'name': 'Charger max current setting'},
    'charger_absolute_max_current': {'unit': AMPERE, 'name': 'Charger absolute max current setting'},
    'cable_lock_mode': {'unit': '', 'name': 'Cable lock mode'},
    'cable_max_current': {'unit': AMPERE, 'name': 'Cable max current'},
    'unlocked_by_card': {'unit': CARD_ID, 'name': 'Card used'},
    'lf_l1': {'unit': PERCENT, 'name': 'Loadfactor L1'},
    'lf_l2': {'unit': PERCENT, 'name': 'Loadfactor L2'},
    'lf_l3': {'unit': PERCENT, 'name': 'Loadfactor L3'},
    'lf_n': {'unit': PERCENT, 'name': 'Loadfactor N'},
    'car_status': {'unit': '', 'name': 'Status'}
}

_sensorStateClass = {
    'energy_total': STATE_CLASS_TOTAL_INCREASING,
    'current_session_charged_energy': STATE_CLASS_TOTAL_INCREASING
}

_sensorDeviceClass = {
    'energy_total': DEVICE_CLASS_ENERGY,
    'current_session_charged_energy': DEVICE_CLASS_ENERGY
}

_sensors = [
    'car_status',
    'charger_max_current',
    'charger_absolute_max_current',
    'charger_err',
    'charger_access',
    'stop_mode',
    'cable_lock_mode',
    'cable_max_current',
    'pre_contactor_l1',
    'pre_contactor_l2',
    'pre_contactor_l3',
    'post_contactor_l1',
    'post_contactor_l2',
    'post_contactor_l3',
    'charger_temp',
    'charger_temp0',
    'charger_temp1',
    'charger_temp2',
    'charger_temp3',
    'current_session_charged_energy',
    'charge_limit',
    'adapter',
    'unlocked_by_card',
    'energy_total',
    'wifi',

    'u_l1',
    'u_l2',
    'u_l3',
    'u_n',
    'i_l1',
    'i_l2',
    'i_l3',
    'p_l1',
    'p_l2',
    'p_l3',
    'p_n',
    'p_all',
    'lf_l1',
    'lf_l2',
    'lf_l3',
    'lf_n',

    'firmware',
    'serial_number',
    'wifi_ssid',
    'wifi_enabled',
    'timezone_offset',
    'timezone_dst_offset',
]


def _create_sensors_for_homeserver(homeserverName, hass):
    entities = []

    for sensor in _sensors:

        _LOGGER.debug(f"adding Sensor: {sensor} for charger {homeserverName}")
        sensorUnit = _sensorUnits.get(sensor).get('unit') if _sensorUnits.get(sensor) else ''
        sensorName = _sensorUnits.get(sensor).get('name') if _sensorUnits.get(sensor) else sensor
        sensorStateClass = _sensorStateClass[sensor] if sensor in _sensorStateClass else ''
        sensorDeviceClass = _sensorDeviceClass[sensor] if sensor in _sensorDeviceClass else ''
        entities.append(
            GoeChargerSensor(
                hass.data[DOMAIN]["coordinator"],
                f"sensor.goecharger_{homeserverName}_{sensor}",
                homeserverName, sensorName, sensor, sensorUnit, sensorStateClass, sensorDeviceClass
            )
        )

    return entities


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    _LOGGER.debug("setup sensors...")
    config = config_entry.as_dict()["data"]

    homeserverName = config[CONF_NAME]

    _LOGGER.debug(f"charger name: '{homeserverName}'")
    async_add_entities(_create_sensors_for_charger(homeserverName, hass))


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up go-eCharger Sensor platform."""
    _LOGGER.debug("setup_platform")
    if discovery_info is None:
        return

    homeservers = discovery_info[CONF_HOMESERVERS]

    entities = []
    for homeserver in homeservers:
        homeserverName = homeserver[0][CONF_NAME]
        _LOGGER.debug(f"homeserver name: '{homeserverName}'")
        entities.extend(_create_sensors_for_homeserver(homeserverName, hass))

    async_add_entities(entities)


class HomserverSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entity_id, homeserverName, name, attribute, unit, stateClass, deviceClass):
        """Initialize the go-eCharger sensor."""

        super().__init__(coordinator)
        self.homeservername = homeserverName
        self.entity_id = entity_id
        self._name = name
        self._attribute = attribute
        self._unit = unit
        self._attr_state_class = stateClass
        self._attr_device_class = deviceClass


    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._homeservername)
            },
            "name": self._homeservername,
            "manufacturer": "Clage",
            "model": "HOMESERVER",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique_id of the sensor."""
        return f"{self._chargername}_{self._attribute}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._chargername][self._attribute]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
