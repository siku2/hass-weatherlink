from weatherlink.units import WindSpeed, UnitConfig

METRIC_CONFIG_JSON = {
    "temperature": "CELSIUS",
    "pressure": "HPA",
    "wind_speed": "KMH",
    "pm": "UG_PER_M3",
    "rain_rate": "MMH",
    "rainfall": "MM",
}


def test_to_json():
    assert UnitConfig.default_metric().as_dict() == METRIC_CONFIG_JSON


def test_from_json():
    assert UnitConfig.from_dict(METRIC_CONFIG_JSON) == UnitConfig.default_metric()

    partial_config_json = METRIC_CONFIG_JSON.copy()
    del partial_config_json["wind_speed"]
    partial_config = UnitConfig.default_metric()
    partial_config.wind_speed = WindSpeed.default()
    assert UnitConfig.from_dict(partial_config_json) == partial_config
