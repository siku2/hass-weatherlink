# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Forgot to update the version in manifest.json all this time

## [0.5.1] - 2021-06-18

### Added

- This changelog

### Fixed

- Polling-based sensors no longer working if real-time broadcast listening is enabled

## [0.5.0] - 2021-06-17

### Added

- Add broadcast listener to receive real-time updates ([#8])

### Changed

- Split WeatherLink API into multiple files to make it more readable

### Fixed

- Entities Becoming Unavailable ([#7])

## [0.4.1] - 2021-05-29

### Fixed

- Broken weather entity

## [0.4.0] - 2021-05-29

### Added

- Make it possible to configure the rounding for measurements,
  including the ability to disable rounding altogether.

## [0.3.0] - 2021-05-25

### Added

- Integration options which allows the following to be configured:
  - Polling interval
  - Unit for various measurements
- "Wind direction" sensor which reports the bearing in text form
  ("N", "E", "S", "W") with 16 values
- Update integration manifest to link to documentation, issue tracker,
  and specify the IoT class

### Changed

- Unit of "UV index" is now `UV index` so that Home Assistant displays it as a
  graph instead of distinct values.

## [0.2.7] - 2021-05-22

### Added

- Update the README to contain installation instructions and a section about
  limitations imposed by WeatherLink
- Handle the case where WeatherLink returns multiple instances of the same data
  structure (split setup) by flattening them into a single one

### Fixed

- Discovered a lot of values which aren't always returned by ([#2])

## [0.2.6] - 2021-05-20

### Added

- "Wind max speed" sensor
  
### Removed

- Removed "high" and "10_min_high" attributes from "Wind speed" sensor.
  Replaced by "Wind max speed"

## [0.2.5] - 2021-05-16

### Added

- "Inside Humidity" sensor
- "last_report_time" to the "AirLink Status" sensor
  
### Changed

- "AirLink Status" sensor now reports either `connected`, `disconnected`, or `unknown`,
  instead of the last report time. The last report time can still be seen in the
  attributes though.
- Adjusted the rounding of some values

### Removed

- "humidity" attribute from "Inside Temperature"
- weather entity can no longer return the `fog` condition because of false-positives

## [0.2.4] - 2021-05-14

### Added

- Separate "Soil Moisture" and "Soil Temperature" sensor

### Removed

- "Soil" sensor, replaced by "Soil Moisture" and "Soil Temperature"

## [0.2.3] - 2021-05-13

### Added

- "Rain rate" sensor separate from the "Rainfall" sensor

### Changed

- Adjust calculation for the current condition of the weather entity
- Consistently use `m³` instead of `m^3` in units
  
### Removed

- "rain rate" attributes from "Rainfall" sensor
  
### Fixed

- "10_min_dir" from the "Wind bearing" sensor is not always sent by WeatherLink.
  If the field was absent it would cause an error.

## [0.2.2] - 2021-05-11

[Unreleased]: https://github.com/siku2/hass-weatherlink/compare/v0.5.0...HEAD
[0.5.1]: https://github.com/siku2/hass-weatherlink/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/siku2/hass-weatherlink/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/siku2/hass-weatherlink/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/siku2/hass-weatherlink/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/siku2/hass-weatherlink/compare/v0.2.7...v0.3.0
[0.2.7]: https://github.com/siku2/hass-weatherlink/compare/v0.2.6...v0.2.7
[0.2.6]: https://github.com/siku2/hass-weatherlink/compare/v0.2.5...v0.2.6
[0.2.5]: https://github.com/siku2/hass-weatherlink/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/siku2/hass-weatherlink/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/siku2/hass-weatherlink/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/siku2/hass-weatherlink/releases/tag/v0.2.2

[#2]:    https://github.com/siku2/hass-weatherlink/issues/2
[#7]:    https://github.com/siku2/hass-weatherlink/issues/7
[#8]:    https://github.com/siku2/hass-weatherlink/issues/8
