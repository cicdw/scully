import geoip2.database as geo_db
import json
import logging
import os
import re
import subprocess
from .stocks import Share
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
        prev_close = stock.get_prev_close()
        return current, prev_close

    def interface(self, *tickers, msg=None):
        try:
            for ticker in tickers:
                current, prev_close = self.get_stock_info(ticker)
                if current is None:
                    resp = "{0} doesn't appear to be actively traded right now.".format(ticker)
                else:
                    resp = "{0} is currently trading at ${1}".format(ticker, current)
                report_msg = self.say(resp, **msg)
                emoji = 'chart_with_upwards_trend' if current > prev_close else 'chart_with_downwards_trend'
                self.react(emoji, **report_msg)
        except:
            self.log.exception('Stock pull failed for ticker {}'.format(ticker))


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


@register(register_help=True, skip_test=True)
class HackerTracker(Interface):

    cmd = 'hack'
    cli_doc = '$ hack reports geolocation information about the last ssh attempt into scully\'s home!'

    def __init__(self, *args, db_path='', **kwargs):
        # https://dev.maxmind.com/geoip/geoip2/geolite2/
        super().__init__(*args, **kwargs)
        try:
            self.db_reader = geo_db.Reader(db_path)
            self.log.info('Reading GeoDB {}'.format(db_path))
        except:
            self.log.exception('Could not read from {}!'.format(db_path))

    @staticmethod
    def get_last_ssh_attempt(n=50):
        bash_cmd = 'journalctl _COMM=sshd -n {}'.format(n)
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        pattern = re.compile('.* Invalid user .* from .*')
        user_patt = re.compile('user (.*?) from')
        ip_patt = re.compile('from (.*?)$')
        hacks = pattern.findall(output.decode())
        last_hack = hacks[-1]
        time, user, ip = last_hack[:15], user_patt.findall(last_hack)[0], ip_patt.findall(last_hack)[0]
        return dict(time=time + ' EST', user=user, ip=ip)

    def interface(self, *tickers, msg=None):
        info = self.get_last_ssh_attempt()
        location = self.db_reader.city(info['ip'])
        city, country = location.city.name, location.country.name
        hack_report = '''Time: {time}\nUsername attempted: {user}\nLocation of IP: {city}, {country}'''.format(time=info['time'],
                                                                                                               user=info['user'],
                                                                                                               city=city,
                                                                                                               country=country)
        self.say(hack_report, **msg)

