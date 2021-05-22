# Home Assistant WeatherLink

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Python 3.8](https://img.shields.io/badge/python-3.8-blue)

A custom component for Davis Instruments' [WeatherLink](https://www.davisinstruments.com/weatherlinklive/) and [AirLink](https://www.davisinstruments.com/airlink/) stations.

## Installation

1. Add this repository as a [Custom repository](https://hacs.xyz/docs/faq/custom_repositories/) to HACS
2. Install the "WeatherLink" integration in HACS
3. Head over to the Home Assistant configuration and set up the integration there

## AirLink

Older versions of the AirLink firmware use a different data structure format when transmitting updates.
This integration currently doesn't support this so in case AirLink isn't working, try updating the firmware.

### AQI

The calculation of AQI varies from country to country and may require inputs that are not available to a single sensor.
For AQI calculations using the latest AQI models.
