import json
import logging
import os
import re
from yahoo_finance import Share
from .core import HELP_REGISTRY, register, Post


class Interface(Post):

    @property
    def prompt(self):
        return re.compile('^\$\s{}'.format(self.cmd))

    def _interface(self, msg):
        text = msg.get('text', '')
        if self.prompt.search(text) and self.user != msg.get('user'):
            _, cmd, *args = text.split()
            self.interface(*args, msg=msg)

    def _reply(self, stream):
        if stream:
            for msg in stream:
                logging.info('Received {}'.format(msg))
                self._interface(msg)

    def __call__(self, stream):
        self._reply(stream)


@register(register_help=True)
class GetTickerPrice(Interface):

    cmd = 'stock'
    cli_doc = '$ stock ticker_1 ticker_2 ... ticker_k reports daily price info for the listed tickers.'

    @staticmethod
    def get_stock_info(ticker):
        stock = Share(ticker)
        current = stock.get_price()
        high, low = stock.get_days_high(), stock.get_days_low()
        prev_close = stock.get_prev_close()
        return current, high, low, prev_close

    def interface(self, *tickers, msg=None):
        try:
            for ticker in tickers:
                current, high, low, prev_close = self.get_stock_info(ticker)
                if current is None:
                    resp = "{0} doesn't appear to be actively traded right now.".format(ticker)
                else:
                    resp = "{0} is currently trading at ${1}, compared with today's high of ${2} and a low of ${3}".format(ticker, current, high, low)
                report_msg = self.say(resp, **msg)
                emoji = 'chart_with_upwards_trend' if current > prev_close else 'chart_with_downwards_trend'
                self.react(emoji, **report_msg)
        except:
            logging.exception('Stock pull failed for ticker {}'.format(ticker))


@register(register_help=True)
class Help(Interface):

    cmd = 'help'
    cli_doc = '$ help [[optional cmd names]] displays help menu for listed commands (which should be separated by spaces)'

    def interface(self, *classes, msg=None):
        classes = HELP_REGISTRY.keys() if len(classes) == 0 else classes
        reply = []
        for c in classes:
            if '```' in c:
                continue
            elif c not in HELP_REGISTRY:
                reply.append('no help available for {}'.format(c))
            else:
                reply.append(HELP_REGISTRY[c])
        fmt_reply = '```' + '\n'.join(reply) + '```'
        self.say(fmt_reply, **msg)


@register()
class Speak(Interface):

    cmd = 'say'
    channel = 'C5AE0R325'

    def interface(self, *phrase, msg=None):
        self.say(' '.join(phrase), channel=self.channel)
