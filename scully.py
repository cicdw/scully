import os
from slackclient import SlackClient
from time import sleep


class Action(object):

    def setup(self):
        pass

    def __init__(self, slack_client):
        self.setup()
        self.slack_client = slack_client

    def __call__(self, stream):
        self.reply(stream)


class AtMentions(Action):

    def setup(self):
        self.AT = '<@U7G9A6Y7R>'

    def reply(self, stream):
        if stream:
            msg = stream[0].get('text', '')
            if self.AT in msg:
                self.slack_client.api_call("chat.postMessage",
                                           channel=stream[0]['channel'],
                                           text='I WANT TO BELIEVE', as_user=True)


class Aliens(Action):

    def reply(self, stream):
        if stream:
            msg = stream[0].get('text', '')
            if 'alien' in msg.lower():
                self.slack_client.api_call("reactions.add",
                                           channel=stream[0]['channel'],
                                           name='alien',
                                           timestamp=stream[0]['ts'], as_user=True)
                self.slack_client.api_call("reactions.add",
                                           channel=stream[0]['channel'],
                                           name='telescope',
                                           timestamp=stream[0]['ts'], as_user=True)


class Scully(object):

    def __init__(self):
        self.slack_client = SlackClient(os.environ.get('SCULLY_TOKEN'))
        self.actions = [AtMentions(self.slack_client), Aliens(self.slack_client)]

    def connect(self):
        self.slack_client.rtm_connect()

    def listen(self):
        sleep(.25)
        incoming = self.slack_client.rtm_read()
        for action in self.actions:
            action(incoming)

    def start(self):
        self.connect()
        while True:
            self.listen()


if __name__ == '__main__':
    bot = Scully()
    bot.start()
