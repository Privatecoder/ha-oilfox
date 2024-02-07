"""The oilfox component."""
from __future__ import annotations
from .OilFox import OilFox
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import update_coordinator
import logging
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD
from .UpdateCoordinator import UpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup OilFox with config entry."""  # noqa: D401
    # _LOGGER.debug("async_setup_entry __init__")

    hass.data.setdefault(DOMAIN, {})
    my_oilfox = OilFox(entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD], "")
    oilfox_data_coordinator = UpdateCoordinator(hass, oilfox_api=my_oilfox)

    await oilfox_data_coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = oilfox_data_coordinator
    await hass.config_entries.async_forward_entry_setups(entry, (Platform.SENSOR,))
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    # for key in entry.options:
    #    _LOGGER.info("%s - %s", key, entry.options[key])


    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # unload_ok = all(
    #    await asyncio.gather(
    #        [hass.config_entries.async_forward_entry_unload(entry, "sensor")]
    #    )
    # )
    # Remove options_update_listener.
    # hass.data[DOMAIN][entry.entry_id]["unsub_options_update_listener"]()
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)

    return True
