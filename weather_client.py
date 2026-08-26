"""Open-Meteoから篠ノ井(長野市)の時間別気温・降水確率を取得する"""

import urllib.request
import json

LATITUDE = 36.55
LONGITUDE = 138.14

URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&hourly=temperature_2m,precipitation_probability"
    "&timezone=Asia%2FTokyo"
    "&forecast_days=1"
)


def fetch_hourly():
    """時刻・気温・降水確率のリスト([{time, temp, rain_prob}, ...])を返す"""
    with urllib.request.urlopen(URL) as res:
        data = json.load(res)

    hourly = data["hourly"]
    return [
        {"time": t, "temp": temp, "rain_prob": rain}
        for t, temp, rain in zip(
            hourly["time"],
            hourly["temperature_2m"],
            hourly["precipitation_probability"],
        )
    ]
