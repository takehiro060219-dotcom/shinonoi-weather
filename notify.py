"""気象データから洗濯・散歩の注意メッセージを組み立てる"""

from weather_client import fetch_hourly
from line_notifier import send_line_broadcast

DAYTIME_START_HOUR = 6
DAYTIME_END_HOUR = 19
RAIN_PROB_THRESHOLD = 30  # % これ以上で洗濯物注意
HOT_TEMP_THRESHOLD = 33  # ℃ これ以上で散歩注意(暑い)

WALK_WINDOW_START_HOUR = 4
WALK_WINDOW_END_HOUR = 22
COMFORTABLE_TEMP_THRESHOLD = 25  # ℃ これ以下かつ雨でなければ散歩お勧め


def is_in_hour_range(time_str, start_hour, end_hour):
    hour = int(time_str.split("T")[1].split(":")[0])
    return start_hour <= hour <= end_hour


def build_hourly_report(hourly):
    lines = ["【篠ノ井 本日の気象情報】"]
    for h in hourly:
        hour = h["time"].split("T")[1][:5]
        lines.append(f"{hour} {h['temp']}℃ 降水{h['rain_prob']}%")
    return "\n".join(lines)


def find_ranges(hours, predicate):
    """predicateを満たす時間帯の連続区間を[(開始idx, 終了idx), ...]で返す。
    終了idxがhoursの長さと同じ場合、区間が観測データの末尾まで続くことを示す"""
    ranges = []
    start = None
    for i, h in enumerate(hours):
        if predicate(h):
            if start is None:
                start = i
        elif start is not None:
            ranges.append((start, i))
            start = None
    if start is not None:
        ranges.append((start, len(hours)))
    return ranges


def format_range(hours, start_idx, end_idx):
    start_label = hours[start_idx]["time"].split("T")[1][:5]
    if end_idx >= len(hours):
        return f"{start_label}以降"
    end_label = hours[end_idx]["time"].split("T")[1][:5]
    return f"{start_label}から{end_label}"


def build_messages(hourly):
    daytime = [
        h for h in hourly if is_in_hour_range(h["time"], DAYTIME_START_HOUR, DAYTIME_END_HOUR)
    ]
    walk_window = [
        h
        for h in hourly
        if is_in_hour_range(h["time"], WALK_WINDOW_START_HOUR, WALK_WINDOW_END_HOUR)
    ]

    messages = []

    rain_ranges = find_ranges(daytime, lambda h: h["rain_prob"] >= RAIN_PROB_THRESHOLD)
    if rain_ranges:
        lines = [
            f"☔ {format_range(daytime, s, e)}は降水確率が高いので洗濯物の外干しに注意してください。"
            for s, e in rain_ranges
        ]
        messages.append("\n".join(lines))

    heat_ranges = find_ranges(daytime, lambda h: h["temp"] >= HOT_TEMP_THRESHOLD)
    if heat_ranges:
        lines = [
            f"🥵 {format_range(daytime, s, e)}は気温が高いので散歩は控えましょう。"
            for s, e in heat_ranges
        ]
        messages.append("\n".join(lines))

    walk_ranges = find_ranges(
        walk_window,
        lambda h: h["temp"] <= COMFORTABLE_TEMP_THRESHOLD and h["rain_prob"] < RAIN_PROB_THRESHOLD,
    )
    if walk_ranges:
        lines = [
            f"🚶 {format_range(walk_window, s, e)}は気温が低いので散歩にお勧めです。"
            for s, e in walk_ranges
        ]
        messages.append("\n".join(lines))

    if not messages:
        messages.append("今日は特に注意事項はありません。")

    return messages


def main():
    hourly = fetch_hourly()
    all_messages = [build_hourly_report(hourly)] + build_messages(hourly)
    for msg in all_messages:
        print(msg)
    send_line_broadcast(all_messages)


if __name__ == "__main__":
    main()
