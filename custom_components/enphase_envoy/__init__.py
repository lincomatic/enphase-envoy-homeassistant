"""The Enphase Envoy integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, DEFAULT_SCAN_INTERVAL, DOMAIN, PATH_HOME, PATH_PRODUCTION

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Enphase Envoy from a config entry."""
    host = entry.data[CONF_HOST]

    coordinator = EnvoyDataUpdateCoordinator(
        hass,
        host=host,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class EnvoyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Envoy data."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
    ) -> None:
        """Initialize."""
        self.host = host
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via web scraping."""
        try:
            data = {}

            # Scrape /home page for System Overview data
            home_url = f"http://{self.host}{PATH_HOME}"
            async with self.session.get(home_url, timeout=10) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching {home_url}: HTTP {response.status}")
                home_html = await response.text()
                data.update(self._parse_home_page(home_html))

            # Scrape /production page for System Energy Production data
            production_url = f"http://{self.host}{PATH_PRODUCTION}"
            async with self.session.get(production_url, timeout=10) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching {production_url}: HTTP {response.status}")
                production_html = await response.text()
                data.update(self._parse_production_page(production_html))

            return data

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Envoy: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error parsing Envoy data: {err}") from err

    def _parse_home_page(self, html: str) -> dict:
        """Parse the /home page for System Overview data."""
        soup = BeautifulSoup(html, "lxml")
        data = {}

        try:
            # Find all table rows and extract data
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # Parse specific metrics
                        if "Lifetime generation" in label:
                            data["lifetime_energy"] = self._parse_energy_value(value)
                        elif "Currently generating" in label:
                            data["current_power"] = self._parse_power_value(value)
                        elif "Number of Microinverters Online" in label:
                            data["inverters_online"] = self._parse_int_value(value)
                        elif "Number of Microinverters" in label and "Online" not in label:
                            data["inverters_total"] = self._parse_int_value(value)
                        elif "Current Software Version" in label:
                            data["software_version"] = value
                        elif "Database Size" in label:
                            data["database_size"] = value
                        elif "Envoy IP Address" in label:
                            data["ip_address"] = value
            
            # Parse status divs
            good_divs = soup.find_all("div", class_="good")
            bad_divs = soup.find_all("div", class_="bad")
            
            data["microinverters_status"] = "online" if any("Microinverters" in div.get_text() for div in good_divs) else "offline"
            data["web_status"] = "online" if any("Web" in div.get_text() for div in good_divs) else "offline"
            
        except Exception as err:
            _LOGGER.warning("Error parsing home page: %s", err)

        _LOGGER.debug("Parsed home page data: %s", data)
        return data

    def _parse_production_page(self, html: str) -> dict:
        """Parse the /production page for System Energy Production data."""
        soup = BeautifulSoup(html, "lxml")
        data = {}

        try:
            # Find all table rows and extract production data
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # Parse specific metrics
                        if label == "Currently":
                            data["current_power_production"] = self._parse_power_value(value)
                        elif label == "Today":
                            data["today_energy"] = self._parse_energy_value(value)
                        elif label == "Past Week":
                            data["week_energy"] = self._parse_energy_value(value)
                        elif label == "Since Installation":
                            data["lifetime_energy_production"] = self._parse_energy_value(value)
            
            # Parse system live since date
            good_divs = soup.find_all("div", class_="good")
            for div in good_divs:
                text = div.get_text(strip=True)
                if any(char.isdigit() for char in text):
                    data["system_live_since"] = text
                    break
                    
        except Exception as err:
            _LOGGER.warning("Error parsing production page: %s", err)

        _LOGGER.debug("Parsed production page data: %s", data)
        return data
    
    def _parse_power_value(self, value: str) -> float | None:
        """Parse power value from string (e.g., '92.8 W' or '1.5 kW')."""
        try:
            value = value.strip().upper()
            if "KW" in value:
                return float(value.replace("KW", "").strip()) * 1000
            elif "W" in value:
                return float(value.replace("W", "").strip())
        except (ValueError, AttributeError) as err:
            _LOGGER.debug("Could not parse power value '%s': %s", value, err)
        return None
    
    def _parse_energy_value(self, value: str) -> float | None:
        """Parse energy value from string (e.g., '11.7 kWh' or '81.1 MWh')."""
        try:
            value = value.strip().upper()
            if "MWH" in value:
                return float(value.replace("MWH", "").strip()) * 1000000
            elif "KWH" in value:
                return float(value.replace("KWH", "").strip()) * 1000
            elif "WH" in value:
                return float(value.replace("WH", "").strip())
        except (ValueError, AttributeError) as err:
            _LOGGER.debug("Could not parse energy value '%s': %s", value, err)
        return None
    
    def _parse_int_value(self, value: str) -> int | None:
        """Parse integer value from string."""
        try:
            return int(value.strip())
        except (ValueError, AttributeError) as err:
            _LOGGER.debug("Could not parse int value '%s': %s", value, err)
        return None
