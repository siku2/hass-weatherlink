# Home Assistant WeatherLink

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Python 3.8](https://img.shields.io/badge/python-3.8-blue)

A custom component for Davis Instruments' [WeatherLink](https://www.davisinstruments.com/weatherlinklive/) and [AirLink](https://www.davisinstruments.com/airlink/) stations.

## Installation

1. Add this repository as a [Custom repository](https://hacs.xyz/docs/faq/custom_repositories/) to HACS
2. Install the "WeatherLink" integration in HACS
3. Head over to the Home Assistant configuration and set up the integration there

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

#### AQI

The calculation of AQI varies from country to country and may require inputs that are not available to a single sensor.
For AQI calculations using the latest AQI models.
