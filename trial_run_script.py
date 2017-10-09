import os
from slackclient import SlackClient

TOKEN = os.environ.get('SCULLY_TOKEN')
AT_BOT = '<@U7G9A6Y7R>'


def parse_incoming(stream):
    if not stream:
        return None, None
    else:
        msg = stream[0].get('text', '')
        if AT_BOT in msg:
            return stream[0]['channel'], 'I WANT TO BELIEVE'
        return None, None


if __name__ == '__main__':
    sc = SlackClient(TOKEN)
    if sc.rtm_connect():
        while True:
            channel_id, msg = parse_incoming(sc.rtm_read())
            if channel_id is not None:
                sc.api_call("chat.postMessage", channel=channel_id,
                            text=msg, as_user=True)
