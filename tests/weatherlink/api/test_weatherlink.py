import json

from weatherlink.api.conditions import (
    CurrentConditions,
    IssCondition,
    LssBarCondition,
    LssTempHumCondition,
)
from weatherlink.api.rest import parse_from_json


def test_parse():
    payload = json.loads(
        """
        {
            "data": {
                "did": "001D0A7139D6",
                "ts": 1610810640,
                "conditions": [
                    {
                        "lsid": 380030,
                        "data_structure_type": 1,
                        "txid": 1,
                        "temp": 26.6,
                        "hum": 96.9,
                        "dew_point": 25.8,
                        "wet_bulb": 26.3,
                        "heat_index": 26.6,
                        "wind_chill": 22.9,
                        "thw_index": 22.9,
                        "thsw_index": 20.9,
                        "wind_speed_last": 5.00,
                        "wind_dir_last": 254,
                        "wind_speed_avg_last_1_min": 3.25,
                        "wind_dir_scalar_avg_last_1_min": 243,
                        "wind_speed_avg_last_2_min": 3.56,
                        "wind_dir_scalar_avg_last_2_min": 245,
                        "wind_speed_hi_last_2_min": 5.00,
                        "wind_dir_at_hi_speed_last_2_min": 246,
                        "wind_speed_avg_last_10_min": 3.18,
                        "wind_dir_scalar_avg_last_10_min": 240,
                        "wind_speed_hi_last_10_min": 7.00,
                        "wind_dir_at_hi_speed_last_10_min": 257,
                        "rain_size": 2,
                        "rain_rate_last": 0,
                        "rain_rate_hi": 0,
                        "rainfall_last_15_min": 0,
                        "rain_rate_hi_last_15_min": 0,
                        "rainfall_last_60_min": 0,
                        "rainfall_last_24_hr": 0,
                        "rain_storm": 0,
                        "rain_storm_start_at": null,
                        "solar_rad": 23,
                        "uv_index": 0.0,
                        "rx_state": 0,
                        "trans_battery_flag": 1,
                        "rainfall_daily": 0,
                        "rainfall_monthly": 276,
                        "rainfall_year": 276,
                        "rain_storm_last": 271,
                        "rain_storm_last_start_at": 1610489461,
                        "rain_storm_last_end_at": 1610809260
                    },
                    {
                        "lsid": 380025,
                        "data_structure_type": 4,
                        "temp_in": 69.7,
                        "hum_in": 24.9,
                        "dew_point_in": 32.2,
                        "heat_index_in": 65.7
                    },
                    {
                        "lsid": 380024,
                        "data_structure_type": 3,
                        "bar_sea_level": 30.239,
                        "bar_trend": -0.028,
                        "bar_absolute": 28.629
                    }
                ]
            },
            "error": null
        }
        """
    )

    data = parse_from_json(CurrentConditions, payload, strict=True)
    assert data[IssCondition]
    assert data[LssTempHumCondition]
    assert data[LssBarCondition]


# see <https://github.com/siku2/hass-weatherlink/issues/2>
def test_parse_02():
    payload = json.loads(
        """
        {
            "data": {
                "did": "001D0A71472B",
                "ts": 1621686244,
                "conditions": [
                    {
                        "lsid": 418773,
                        "data_structure_type": 1,
                        "txid": 1,
                        "temp": 52.1,
                        "hum": 59.1,
                        "dew_point": 38.2,
                        "wet_bulb": 43.9,
                        "heat_index": 51.1,
                        "wind_chill": null,
                        "thw_index": null,
                        "thsw_index": null,
                        "wind_speed_last": null,
                        "wind_dir_last": null,
                        "wind_speed_avg_last_1_min": null,
                        "wind_dir_scalar_avg_last_1_min": null,
                        "wind_speed_avg_last_2_min": null,
                        "wind_dir_scalar_avg_last_2_min": null,
                        "wind_speed_hi_last_2_min": null,
                        "wind_dir_at_hi_speed_last_2_min": null,
                        "wind_speed_avg_last_10_min": null,
                        "wind_dir_scalar_avg_last_10_min": null,
                        "wind_speed_hi_last_10_min": null,
                        "wind_dir_at_hi_speed_last_10_min": null,
                        "rain_size": 2,
                        "rain_rate_last": 0,
                        "rain_rate_hi": 0,
                        "rainfall_last_15_min": 0,
                        "rain_rate_hi_last_15_min": 0,
                        "rainfall_last_60_min": 0,
                        "rainfall_last_24_hr": 54,
                        "rain_storm": 213,
                        "rain_storm_start_at": 1621054081,
                        "solar_rad": 283,
                        "uv_index": null,
                        "rx_state": 0,
                        "trans_battery_flag": 0,
                        "rainfall_daily": 30,
                        "rainfall_monthly": 251,
                        "rainfall_year": 251,
                        "rain_storm_last": 38,
                        "rain_storm_last_start_at": 1620901021,
                        "rain_storm_last_end_at": 1621044061
                    },
                    {
                        "lsid": 418774,
                        "data_structure_type": 1,
                        "txid": 2,
                        "temp": null,
                        "hum": null,
                        "dew_point": null,
                        "wet_bulb": null,
                        "heat_index": null,
                        "wind_chill": null,
                        "thw_index": null,
                        "thsw_index": null,
                        "wind_speed_last": 3.00,
                        "wind_dir_last": 252,
                        "wind_speed_avg_last_1_min": 1.18,
                        "wind_dir_scalar_avg_last_1_min": 251,
                        "wind_speed_avg_last_2_min": 1.00,
                        "wind_dir_scalar_avg_last_2_min": 251,
                        "wind_speed_hi_last_2_min": 4.00,
                        "wind_dir_at_hi_speed_last_2_min": 250,
                        "wind_speed_avg_last_10_min": 2.56,
                        "wind_dir_scalar_avg_last_10_min": 254,
                        "wind_speed_hi_last_10_min": 10.00,
                        "wind_dir_at_hi_speed_last_10_min": 266,
                        "rain_size": 1,
                        "rain_rate_last": 0,
                        "rain_rate_hi": 0,
                        "rainfall_last_15_min": 0,
                        "rain_rate_hi_last_15_min": 0,
                        "rainfall_last_60_min": 0,
                        "rainfall_last_24_hr": 0,
                        "rain_storm": null,
                        "rain_storm_start_at": null,
                        "solar_rad": null,
                        "uv_index": null,
                        "rx_state": 0,
                        "trans_battery_flag": 0,
                        "rainfall_daily": 0,
                        "rainfall_monthly": 0,
                        "rainfall_year": 0,
                        "rain_storm_last": null,
                        "rain_storm_last_start_at": null,
                        "rain_storm_last_end_at": null
                    },
                    {
                        "lsid": 418764,
                        "data_structure_type": 4,
                        "temp_in": 74.4,
                        "hum_in": 41.0,
                        "dew_point_in": 49.2,
                        "heat_index_in": 73.5
                    },
                    {
                        "lsid": 418763,
                        "data_structure_type": 3,
                        "bar_sea_level": 29.660,
                        "bar_trend": 0.054,
                        "bar_absolute": 29.259
                    }
                ]
            },
            "error": null
        }
        """
    )

    data = parse_from_json(CurrentConditions, payload, strict=True)
    assert data[IssCondition]
    assert data[LssTempHumCondition]
    assert data[LssBarCondition]

    assert data[IssCondition].wind_dir_last == 252
