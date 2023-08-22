# Home Assistant WeatherLink

[![GitHub Release](https://img.shields.io/github/release/siku2/hass-weatherlink.svg?style=for-the-badge)](https://github.com/siku2/hass-weatherlink/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/siku2/hass-weatherlink.svg?style=for-the-badge)](https://github.com/siku2/hass-weatherlink/commits/main)
[![License](https://img.shields.io/github/license/siku2/hass-weatherlink.svg?style=for-the-badge)](LICENSE)

[![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://hacs.xyz/docs/faq/custom_repositories)

_Bringing support for Davis Instruments' [WeatherLink](https://www.davisinstruments.com/weatherlinklive) and [AirLink](https://www.davisinstruments.com/airlink) stations to Home Assistant._

## Installation

1. Add this repository as a custom repository to HACS: [![Add Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=siku2&repository=hass-weatherlink&category=integration)
2. Use HACS to install the integration.
3. Restart Home Assistant.
4. Set up the integration using the UI: [![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=weatherlink)

## Limitations

WeatherLink groups data into multiple data structures. For instance, all the data reported by the ISS outdoor station (temperature, wind, rain, solar, etc.) is reported in a single data structure.
When the integration polls the API, it receives a list of these data structures.
It's possible for WeatherLink to report multiple instances of the same data structure. This happens, for instance, when you physically separate parts of the ISS and use multiple channels.
This integration doesn't handle this case very well. If it receives multiple instances of the same data structure,
it primarily uses the first one and only uses the subsequent ones to fill holes in the first one.
If you're running into a problem that's caused by this behaviour, please open an issue.

### AirLink

Older versions of the AirLink firmware use a different data structure format when transmitting updates.
This integration currently doesn't support this so in case AirLink isn't working, try updating the firmware.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)
