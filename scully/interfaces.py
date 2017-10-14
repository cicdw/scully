import json
import logging
import os
import re
from yahoo_finance import Share
from .core import Post


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
                if hasattr(self, 'cmd'):
                    self._interface(msg)
                else:
                    self.reply(msg)

    def __call__(self, stream):
        self._reply(stream)


#class Help(Response):
#
#    cmd = 'help'
#    def interface(self, *args, msg=None):
#        for resp in Response.__subclasses__():
#            if hasattr(resp, 'cmd') and resp.cmd == args[0]:
#                self.say(resp.cli_doc, **msg)
#            elif len(args) == 0:
#                self.say('no help available', **msg)
#
#
#class GetTickerPrice(Response):
#
#    cmd = 'stock'
#    cli_doc = '$ stock ticker1 ticker2 ... tickerk reports daily price info for the listed tickers.'
#
#    def interface(self, *tickers, msg=None):
#        try:
#            for ticker in tickers:
#                stock = Share(ticker)
#                current = stock.get_price()
#                high, low = stock.get_days_high(), stock.get_days_low()
#                prev_close = stock.get_prev_close()
#                if current is None:
#                    resp = "{0} doesn't appear to be actively traded right now.".format(ticker)
#                else:
#                    resp = "{0} is currently trading at ${1}, compared with today's high of ${2} and a low of ${3}".format(ticker, current, high, low)
#                report_msg = self.say(resp, **msg)
#                emoji = 'chart_with_upwards_trend' if current > prev_close else 'chart_with_downwards_trend'
#                self.react(emoji, **report_msg)
#        except:
#            logging.error('Stock pull failed for ticker {}'.format(ticker))
