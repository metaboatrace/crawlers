import io
import logging
import os

import requests
from cachetools import TTLCache, cached
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()


cache: TTLCache[str, str] = TTLCache(maxsize=10000, ttl=3600)  # サイズを増やして並列処理に対応


@cached(cache)
def _fetch_html_text(url: str) -> str:
    try:
        # タイムアウトを設定し、リトライを実装
        response = requests.get(
            url,
            timeout=30,  # 30秒のタイムアウト
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        # タイムアウト時はキャッシュしない
        raise
    except requests.exceptions.RequestException:
        # その他のリクエストエラーもキャッシュしない
        raise


def fetch_html_as_io(url: str) -> io.StringIO:
    return io.StringIO(_fetch_html_text(url))


def send_slack_notification(message: str) -> None:
    """Send a notification to Slack using the configured webhook URL."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL", "#999-notice-dev")

    if not slack_token:
        logger = logging.getLogger(__name__)
        logger.warning("SLACK_BOT_TOKEN not set. Skipping Slack notification.")
        return

    try:
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel=slack_channel, text=message)
    except SlackApiError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending Slack notification: {e.response['error']}")
