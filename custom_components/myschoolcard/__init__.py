"""Custom integration to integrate MySchoolCard with Home Assistant."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    ISSUE_URL,
    VERSION,
)

SCAN_INTERVAL = timedelta(minutes=5)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Disallow configuration via YAML."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Load the saved entities."""
    _LOGGER.info(
        "Version %s is starting, if you have any issues please report them here: %s",
        VERSION,
        ISSUE_URL,
    )

    config_entry.add_update_listener(update_listener)

    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    if unloaded:
        _LOGGER.info("Successfully removed sensor from the %s integration", DOMAIN)
    return unloaded


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
