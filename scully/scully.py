import logging
import os
from slackclient import SlackClient
import sys
from time import sleep

from .core import REGISTRY


LOG_FILE = os.path.expanduser('~/scully.log')


class Scully(object):

    RATE_LIMIT = 0.25

    def __init__(self, fname=None, client=SlackClient):
        self.logging(fname=fname)
        logging.info('Starting Scully bot!')
        self.slack_client = client(os.environ.get('SCULLY_TOKEN'))
        self.responses = []

        for resp in REGISTRY:
            init = resp(self.slack_client)
            self.responses.append(init)
            logging.info('Registered {}'.format(init.name))

    def logging(self, fname=None):
        logging.basicConfig(filename=fname,
                            format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.DEBUG)

    def connect(self):
        self.slack_client.rtm_connect()

    def listen(self):
        incoming = self.slack_client.rtm_read()
        if incoming:
            logging.info('Received {}'.format(incoming))
        for resp in self.responses:
            resp(incoming)

    def start(self, stop_after=None):
        self.connect()
        logging.info('Scully is connected.')
        end_iter = 0 if stop_after is None else stop_after
        while not end_iter:
            sleep(self.RATE_LIMIT)
            self.listen()
            end_iter = max(end_iter - 1, 0)


def run():
    verbose = sys.argv[-1]
    fname = LOG_FILE if verbose == '-v' else None
    bot = Scully(fname=fname)
    logging.info('Scully initialized.')
    try:
        bot.start()
    except Exception:
        logging.exception("Scully has been killed!")
