import os
from slackclient import SlackClient
from time import sleep

class Scully(object):

    def __init__(self):
        self.slack_client = SlackClient(os.environ.get('SCULLY_TOKEN'))
        self.AT = '<@U7G9A6Y7R>'

    def connect(self):
        self.slack_client.rtm_connect()

    def listen(self):
        sleep(.25)
        return self.slack_client.rtm_read()

    def start(self):
        while True:
            channel_id, msg = self.parse_incoming(self.listen())
            if channel_id is not None:
                self.slack_client.api_call("chat.postMessage", channel=channel_id,
                            text=msg, as_user=True)

    def parse_incoming(self, stream):
        if not stream:
            return None, None
        else:
            msg = stream[0].get('text', '')
            if self.AT in msg:
                return stream[0]['channel'], 'I WANT TO BELIEVE'
            return None, None


if __name__ == '__main__':
    bot = Scully()
    bot.connect()
    bot.start()
