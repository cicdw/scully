import os
from slackclient import SlackClient
from time import sleep


class Response(object):

    def setup(self):
        pass

    def reply(self, msg):
        raise NotImplementedError

    def __init__(self, slack_client):
        self.setup()
        self.slack_client = slack_client

    def _reply(self, stream):
        if stream:
            for msg in stream:
                self.reply(msg)

    def __call__(self, stream):
        self._reply(stream)


class AtMentions(Response):

    def setup(self):
        self.AT = '<@U7G9A6Y7R>'

    def reply(self, msg):
        text = msg.get('text', '')
        if self.AT in text:
            self.slack_client.api_call("chat.postMessage",
                                        channel=msg['channel'],
                                        text='I WANT TO BELIEVE', as_user=True)


class Aliens(Response):

    def reply(self, msg):
        text = msg.get('text', '')
        if 'alien' in text.lower():
            self.slack_client.api_call("reactions.add",
                                        channel=msg['channel'],
                                        name='alien',
                                        timestamp=msg['ts'], as_user=True)
            self.slack_client.api_call("reactions.add",
                                        channel=msg['channel'],
                                        name='telescope',
                                        timestamp=msg['ts'], as_user=True)


class Scully(object):

    def __init__(self, client=SlackClient):
        self.slack_client = client(os.environ.get('SCULLY_TOKEN'))
        self.responses = []
        for resp in Response.__subclasses__():
            self.responses.append(resp(self.slack_client))

    def connect(self):
        self.slack_client.rtm_connect()

    def listen(self):
        sleep(.25)
        incoming = self.slack_client.rtm_read()
        for resp in self.responses:
            resp(incoming)

    def start(self):
        self.connect()
        while True:
            self.listen()


if __name__ == '__main__':
    bot = Scully()
    bot.start()
