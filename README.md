# Enphase Envoy Home Assistant Integration

A custom Home Assistant integration for older Enphase Envoy models that lack a REST API. It uses web scraping to extract data from the Envoy's web interface.

## Features

- Scrapes data from Envoy-R web interface (no API required)
- Works with older Envoy models running firmware before 3.9 which lack a REST API
- Tested on my Envoy running firmware R3.7.31
- Real-time solar production monitoring
- Energy consumption tracking
- Daily and lifetime production statistics
- Easy configuration through Home Assistant UI
- No authentication required

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/enphase_envoy` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Enphase Envoy"
4. Enter your Envoy device details:
   - **Host**: IP address or hostname of your Envoy device (e.g., 192.168.1.53)

## Sensors

This integration scrapes data from two pages:
- `/home` - System Overview data
- `/production` - System Energy Production data

### Power Sensors
- **Current Power** - Currently generating power from /home page (W)
- **Current Power Production** - Currently generating power from /production page (W)

### Energy Sensors
- **Today Energy** - Energy produced today (Wh)
- **Week Energy** - Energy produced in the past week (Wh)
- **Lifetime Energy** - Total energy produced since installation from /home page (Wh)
- **Lifetime Energy Production** - Total energy produced since installation from /production page (Wh)

### System Information Sensors
- **Inverters Online** - Number of microinverters currently online
- **Inverters Total** - Total number of microinverters
- **Software Version** - Current Envoy software version
- **Database Size** - Current database usage
- **IP Address** - Envoy IP address
- **Microinverters Status** - Connection status to microinverters (online/offline)
- **Web Status** - Connection status to web (online/offline)
- **System Live Since** - Date and time when system went live

## Requirements

- Home Assistant 2023.1 or newer
- Enphase Envoy-R device on your local network
- Network access to the Envoy web interface (typically port 80)
- beautifulsoup4 and lxml libraries (automatically installed)

## Support

For issues, feature requests, or questions, please open an issue on GitHub.

## License

This project is licensed under the MIT License.

## Credits

Developed for the Home Assistant community.
