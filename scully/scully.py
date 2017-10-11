import os
from slackclient import SlackClient
from time import sleep

from .responses import Response


class Scully(object):

    RATE_LIMIT = 0.25

    def __init__(self, client=SlackClient):
        self.slack_client = client(os.environ.get('SCULLY_TOKEN'))
        self.responses = []
        for resp in Response.__subclasses__():
            self.responses.append(resp(self.slack_client))

    def connect(self):
        self.slack_client.rtm_connect()

    def listen(self):
        incoming = self.slack_client.rtm_read()
        for resp in self.responses:
            resp(incoming)

    def start(self, stop_after=None):
        self.connect()
        end_iter = 0 if stop_after is None else stop_after
        while not end_iter:
            sleep(self.RATE_LIMIT)
            self.listen()
            end_iter = max(end_iter - 1, 0)


def run():
    bot = Scully()
    bot.start()
