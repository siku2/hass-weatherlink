import json

from weatherlink.api import AirQualityCondition, CurrentConditions, get_data_from_body

SAMPLE_RESPONSE = json.loads(
    """
{
    "data": {
        "did": "001D0A10064A",
        "name": "Luftqualität",
        "ts": 1610810072,
        "conditions": [
            {
                "lsid": 381867,
                "data_structure_type": 6,
                "temp": 27.6,
                "hum": 87.1,
                "dew_point": 24.2,
                "wet_bulb": 26.3,
                "heat_index": 27.4,
                "pm_1_last": 28,
                "pm_2p5_last": 47,
                "pm_10_last": 57,
                "pm_1": 25.87,
                "pm_2p5": 48.55,
                "pm_2p5_last_1_hour": 47.92,
                "pm_2p5_last_3_hours": 47.24,
                "pm_2p5_last_24_hours": 37.35,
                "pm_2p5_nowcast": 47.45,
                "pm_10": 59.28,
                "pm_10_last_1_hour": 58.68,
                "pm_10_last_3_hours": 57.82,
                "pm_10_last_24_hours": 43.66,
                "pm_10_nowcast": 58.15,
                "last_report_time": 1610810072,
                "pct_pm_data_last_1_hour": 100,
                "pct_pm_data_last_3_hours": 100,
                "pct_pm_data_nowcast": 100,
                "pct_pm_data_last_24_hours": 100
            }
        ]
    },
    "error": null
}
"""
)


def test_parse():
    data = CurrentConditions.from_json(get_data_from_body(SAMPLE_RESPONSE), strict=True)
    assert data[AirQualityCondition]
