import logging
import os
from slackclient import SlackClient
import sys
from time import sleep

from .responses import Response


LOG_FILE = os.path.expanduser('~/scully_logs.txt')

class Scully(object):

    RATE_LIMIT = 0.25

    def __init__(self, client=SlackClient):
        self.slack_client = client(os.environ.get('SCULLY_TOKEN'))
        self.responses = []
        for resp in Response.__subclasses__():
            self.responses.append(resp(self.slack_client))
            logging.info('Registered {}'.format(resp.__name__))

    def connect(self):
        self.slack_client.rtm_connect()

    def listen(self):
        incoming = self.slack_client.rtm_read()
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
    logging.basicConfig(filename=fname,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
    logging.info('Starting Scully bot!')
    bot = Scully()
    logging.info('Scully initialized.')
    try:
        bot.start()
    except Exception:
        logging.exception("Scully has been killed!")
