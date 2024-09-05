"""Sensor platform for MySchoolCard."""
import datetime
import logging
from datetime import timedelta

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .api import MySchoolCard
from .const import (
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    config = {
        CONF_USERNAME: entry.data[CONF_USERNAME],
        CONF_PASSWORD: entry.data[CONF_PASSWORD],
    }

    sensors = []
    msc = MySchoolCard(config.get(CONF_USERNAME), config.get(CONF_PASSWORD))
    cards = await hass.async_add_executor_job(msc.get_all_data)
    for card in cards:
        sensors.append(MySchoolCardSensor(hass, config, msc, card))

    async_add_entities(sensors, True)


class MySchoolCardSensor(Entity):
    def __init__(self, hass, config, msc, card):
        """Initialize the sensor"""
        self._name = None
        self._icon = "mdi:cash"
        self._device_class = "monetary"
        self._unit_of_measurement = "RUB"
        self._state = None
        self._data = None
        self.card_id = card
        self.balance = None
        self.line_name = None
        self.docnumber = None
        #        self.msc = msc
        self.config = config
        self.last_updated = None
        self._scan_interval = timedelta(minutes=DEFAULT_SCAN_INTERVAL)
        self.hass = hass

        _LOGGER.debug("Config scan interval: %s", self._scan_interval)

        self.async_update = Throttle(self._scan_interval)(self.async_update)

    @property
    def unique_id(self):
        """
        Return a unique, Home Assistant friendly identifier for this entity.
        """
        return f"{DEFAULT_NAME}_{self.card_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"MySchoolCard {self.line_name} Card"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device_class of this entity, if any."""
        return self._device_class

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        attr = {}
        attr["name"] = self.data["line_name"]
        attr["docnumber"] = self.data["docnumber"]
        attr["balance"] = self._state
        attr["year_tarif"] = str(self.data["yearpayment"]) + " RUB"
        attr["transport_tarif"] = str(self.data["tctarif"]) + " RUB"
        attr["last_updated"] = self.last_updated

        return attr

    async def async_update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        msc = MySchoolCard(
            self.config.get(CONF_USERNAME), self.config.get(CONF_PASSWORD)
        )

        login = await self.hass.async_add_executor_job(msc.login)
        if login:
            data = await self.hass.async_add_executor_job(msc.get_all_data)
            self.data = data.get(self.card_id)
            if float(self.data["balance"]):
                self._state = self.data["balance"]
                self.line_name = self.data["line_name"]
                self.docnumber = self.data["docnumber"]
                self.last_updated = self.update_time()
            else:
                _LOGGER.error("Unable to update data")
        else:
            _LOGGER.error("Invalid Credentials")

    def update_time(self):
        """gets update time"""
        updated = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

        return updated
