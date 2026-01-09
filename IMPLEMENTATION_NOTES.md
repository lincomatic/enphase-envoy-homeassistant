# Implementation Notes

## Web Scraping Approach

This integration uses web scraping to extract data from the Envoy-R web interface, specifically designed for older firmware versions that don't support modern APIs.

### Pages Scraped

1. **`http://192.168.1.53/home`** - System Overview
   - Lifetime generation
   - Currently generating power
   - Number of microinverters (online/total)
   - Software version
   - Database size
   - IP address
   - Connection status (microinverters and web)

2. **`http://192.168.1.53/production`** - System Energy Production
   - Currently generating power
   - Today's production
   - Past week production
   - Lifetime production
   - System live since date

### Data Parsing

The integration uses BeautifulSoup4 with lxml parser to extract data from HTML tables and div elements:

- **Power values**: Parsed from strings like "92.8 W" or "1.5 kW" and converted to watts
- **Energy values**: Parsed from strings like "11.7 kWh" or "81.1 MWh" and converted to watt-hours
- **Status indicators**: Extracted from div elements with `class="good"` or `class="bad"`
- **System info**: Extracted from table rows with label/value pairs

### No Authentication Required

This integration is designed for Envoy-R devices that don't require login credentials. The configuration flow only asks for the host IP address.

### Update Interval

Data is fetched every 60 seconds (configurable via `DEFAULT_SCAN_INTERVAL` in `const.py`).

## Testing

To test the integration:
1. Copy the `custom_components/enphase_envoy` folder to your Home Assistant config
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Enphase Envoy"
5. Enter your Envoy IP address (e.g., 192.168.1.53)

## Customization

If your Envoy-R has different HTML structure, you may need to modify the parsing logic in:
- `_parse_home_page()` method in `__init__.py`
- `_parse_production_page()` method in `__init__.py`

Enable debug logging to see what data is being extracted:
```yaml
logger:
  default: info
  logs:
    custom_components.enphase_envoy: debug
```
