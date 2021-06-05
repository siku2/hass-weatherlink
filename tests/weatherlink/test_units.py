from weatherlink.units import Unit, UnitConfig, WindSpeed

METRIC_CONFIG_JSON = {
    "pm": {"key": "UG_PER_M3", "ndigits": 2},
    "pressure": {"key": "HPA", "ndigits": 0},
    "rain_rate": {"key": "MMH", "ndigits": 1},
    "rainfall": {"key": "MM", "ndigits": 1},
    "temperature": {"key": "CELSIUS", "ndigits": 1},
    "wind_speed": {"key": "KMH", "ndigits": 1},
}


def test_to_json():
    assert UnitConfig.default_metric().as_dict() == METRIC_CONFIG_JSON


def test_from_json():
    assert UnitConfig.from_dict(METRIC_CONFIG_JSON) == UnitConfig.default_metric()

    partial_config_json = METRIC_CONFIG_JSON.copy()
    del partial_config_json["wind_speed"]
    partial_config = UnitConfig.default_metric()
    partial_config.wind_speed = Unit.from_unit_info(WindSpeed.default())
    assert UnitConfig.from_dict(partial_config_json) == partial_config
