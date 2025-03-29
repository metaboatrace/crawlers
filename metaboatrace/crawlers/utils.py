import io
import os

import requests

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()


def fetch_html_as_io(url: str) -> io.StringIO:
    response = requests.get(url)
    response.raise_for_status()
    return io.StringIO(response.text)


def send_slack_notification(message: str) -> None:
    """Send a notification to Slack using the configured webhook URL."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL", "#999-notice-dev")

    if not slack_token:
        print("Warning: SLACK_BOT_TOKEN not set. Skipping Slack notification.")
        return

    try:
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel=slack_channel, text=message)
    except SlackApiError as e:
        print(f"Error sending Slack notification: {e.response['error']}")
