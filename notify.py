"""気象データから洗濯・散歩の注意メッセージを組み立てる"""

from weather_client import fetch_hourly
from line_notifier import send_line_broadcast

WINDOW_START_HOUR = 6
WINDOW_END_HOUR = 18

LAUNDRY_RAIN_THRESHOLD = 40  # % これ以上で外干し注意

WALK_TEMP_THRESHOLD = 28  # ℃ これ未満で散歩快適
WALK_RAIN_THRESHOLD = 50  # % これ未満で散歩快適


def is_in_window(time_str):
    hour = int(time_str.split("T")[1].split(":")[0])
    return WINDOW_START_HOUR <= hour <= WINDOW_END_HOUR


def hour_label(h):
    return h["time"].split("T")[1][:5]


def build_hourly_report(hourly):
    lines = ["【篠ノ井 本日の気象情報】"]
    for h in hourly:
        lines.append(f"{hour_label(h)} {h['temp']}℃ 降水{h['rain_prob']}%")
    return "\n".join(lines)


def find_ranges(hours, predicate):
    """predicateを満たす時間帯の連続区間を[(開始idx, 終了idx), ...]で返す(終了idxは含まない)"""
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
    return f"{hour_label(hours[start_idx])}～{hour_label(hours[end_idx - 1])}"


def build_laundry_message(window):
    flags = [h["rain_prob"] >= LAUNDRY_RAIN_THRESHOLD for h in window]

    if all(flags):
        return "☔ 今日は一日雨なので外干しは控えましょう。"
    if not any(flags):
        return "☀️ 今日は一日晴れています。外干し日和です。"

    lines = [
        f"☔ {format_range(window, s, e)}は降水確率が高いので外干しに注意してください。"
        for s, e in find_ranges(window, lambda h: h["rain_prob"] >= LAUNDRY_RAIN_THRESHOLD)
    ]
    return "\n".join(lines)


def build_walk_message(window):
    def comfortable(h):
        return h["temp"] < WALK_TEMP_THRESHOLD and h["rain_prob"] < WALK_RAIN_THRESHOLD

    flags = [comfortable(h) for h in window]

    if all(flags):
        return "🚶 今日は一日お散歩日和です。"
    if not any(flags):
        return "🏠 今日は一日散歩は控え室内で過ごしましょう。"

    lines = [
        f"🚶 {format_range(window, s, e)}は気温が低いので散歩におすすめです。"
        for s, e in find_ranges(window, comfortable)
    ]
    return "\n".join(lines)


def build_messages(hourly):
    window = [h for h in hourly if is_in_window(h["time"])]
    return [build_laundry_message(window), build_walk_message(window)]


def main():
    hourly = fetch_hourly()
    all_messages = [build_hourly_report(hourly)] + build_messages(hourly)
    for msg in all_messages:
        print(msg)
    send_line_broadcast(all_messages)


if __name__ == "__main__":
    main()
