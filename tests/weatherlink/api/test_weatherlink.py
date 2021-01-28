import json

from weatherlink.api import (
    CurrentConditions,
    IssCondition,
    LssBarCondition,
    LssTempHumCondition,
    get_data_from_body,
)

SAMPLE_RESPONSE = json.loads(
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


def test_parse():
    data = CurrentConditions.from_json(get_data_from_body(SAMPLE_RESPONSE), strict=True)
    assert data[IssCondition]
    assert data[LssTempHumCondition]
    assert data[LssBarCondition]
