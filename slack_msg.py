from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from secret import slack_key

# class slackmessage:
client = WebClient(token=slack_key)

def message(chat, text):
    try:
        response = client.chat_postMessage(channel=chat, text=text)
        assert response["message"]["text"] == text
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")