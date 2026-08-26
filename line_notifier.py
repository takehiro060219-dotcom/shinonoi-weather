"""LINE Messaging APIのブロードキャスト送信でメッセージを届ける"""

import os
import json
import urllib.request

BROADCAST_URL = "https://api.line.me/v2/bot/message/broadcast"


def send_line_broadcast(messages):
    """messages: 文字列のリスト。友だち全員(=自分)に配信する"""
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        raise RuntimeError(
            "環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されていません。"
        )

    body = json.dumps(
        {"messages": [{"type": "text", "text": msg} for msg in messages]}
    ).encode("utf-8")

    req = urllib.request.Request(
        BROADCAST_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    with urllib.request.urlopen(req) as res:
        return res.status
