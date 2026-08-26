"""篠ノ井(長野市)の時間別気温・降水確率を表形式で確認するスクリプト"""

from weather_client import fetch_hourly, LATITUDE, LONGITUDE


def main():
    hourly = fetch_hourly()

    print(f"取得地点: 緯度{LATITUDE}, 経度{LONGITUDE}")
    print(f"{'時刻':<18}{'気温(℃)':<10}{'降水確率(%)'}")
    for h in hourly:
        print(f"{h['time']:<18}{h['temp']:<10}{h['rain_prob']}")


if __name__ == "__main__":
    main()
