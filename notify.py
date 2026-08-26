"""気象データから洗濯・散歩の注意メッセージを組み立てる"""

from weather_client import fetch_hourly
from line_notifier import send_line_broadcast

DAYTIME_START_HOUR = 6
DAYTIME_END_HOUR = 19
RAIN_PROB_THRESHOLD = 30  # % これ以上で洗濯物注意
HOT_TEMP_THRESHOLD = 33  # ℃ これ以上で散歩注意


def is_daytime(time_str):
    hour = int(time_str.split("T")[1].split(":")[0])
    return DAYTIME_START_HOUR <= hour <= DAYTIME_END_HOUR


def build_messages(hourly):
    daytime = [h for h in hourly if is_daytime(h["time"])]

    max_rain_prob = max(h["rain_prob"] for h in daytime)
    max_temp = max(h["temp"] for h in daytime)

    messages = []
    if max_rain_prob >= RAIN_PROB_THRESHOLD:
        messages.append(
            f"☔ 日中の降水確率が最大{max_rain_prob}%です。洗濯物の外干しに注意してください。"
        )
    if max_temp >= HOT_TEMP_THRESHOLD:
        messages.append(
            f"🥵 日中の最高気温は{max_temp}℃の予報です。暑さが厳しいため散歩は控えめにしましょう。"
        )
    if not messages:
        messages.append("今日は特に注意事項はありません。")

    return messages


def main():
    hourly = fetch_hourly()
    messages = build_messages(hourly)
    for msg in messages:
        print(msg)
    send_line_broadcast(messages)


if __name__ == "__main__":
    main()
