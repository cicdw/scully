import json
import logging
import os
import re
import schedule
from yahoo_finance import Share
from .core import HELP_REGISTRY, Post, register
from .interfaces import Interface

CACHE_FILE = os.environ.get('SCULLY_EMOJI_CACHE')


class Response(Post):

    def reply(self, msg):
        raise NotImplementedError

    def _reply(self, stream):
        if stream:
            for msg in stream:
                self.reply(msg)

    def __call__(self, stream):
        self._reply(stream)


@register(register_help=True)
class AddReaction(Response, Interface):

    cmd = 'react'
    cli_doc = '$ react "new_pattern" :emoji: adds :emoji: reaction to all future occurences of "new_pattern"'

    call_signature = re.compile('scully.*react to ".+" with :.*:', re.IGNORECASE)
    ignore_pattern = re.compile('"+\s*"+')
    match_string = re.compile('".+"')
    emoji_string = re.compile(':.*:')

    def __init__(self, slack_client, fname=CACHE_FILE):
        super().__init__(slack_client)
        if fname is not None and os.path.exists(fname):
            self._cache = self.load(fname=fname)
            logging.info('Loaded emoji reactions cache from {}'.format(fname))
        else:
            self._cache = {}
            logging.info('Starting fresh emoji reactions cache.')

        self.fname = fname

    def load(self, fname=CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            out = json.load(f)
        return out

    def save(self):
        if self.fname is not None:
            with open(self.fname, 'w') as f:
                json.dump(self._cache, f)

    def add_reaction(self, listen_for, react_with):
        logging.info('{0}: Storing reaction {1} for pattern "{2}"'.format(self.name, react_with, listen_for))
        self._cache[listen_for] = react_with
        self.save()
        return listen_for, react_with

    def reply(self, msg):
        self._interface(msg) # hack to allow multiple types of use
        text = self.sanitize(msg.get('text', ''))
        reactions = [emoji for t, emoji in self._cache.items() if t.lower() in text.lower()]
        if self.call_signature.search(text) and not self.ignore_pattern.search(text):
            listen_for = self.match_string.search(text).group().replace('"', '').strip()
            react_with = self.emoji_string.search(text).group().replace(':', '')
            self.add_reaction(listen_for, react_with)
            success_msg = self.say('--reaction added for "{}"--'.format(listen_for), **msg)
            self.react(react_with, **success_msg)

        if reactions:
            for emoji in reactions:
                self.react(emoji, **msg)

    def interface(self, *args, msg=None):
        p, e = args[:2]
        if not self.match_string.search(self.sanitize(p)):
            return
        if not self.emoji_string.search(e):
            return
        listen_for = self.match_string.search(self.sanitize(p)).group().replace('"', '').strip()
        react_with = self.emoji_string.search(e).group().replace(':', '')
        self.add_reaction(listen_for, react_with)
        success_msg = self.say('--reaction added for "{}"--'.format(listen_for), **msg)
        self.react(react_with, **success_msg)


@register()
class Monday(Response):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        schedule.every().monday.at("9:00").do(self.do)

    def reply(self, *args):
        pass

    def do(self):
        self.say("Monday, amiright?? :coffeeparrot:", channel='C5AE0R325')


@register()
class AtMentions(Response):

    def reply(self, msg):
        text = msg.get('text', '')
        if self.AT in text:
            self.say('I WANT TO BELIEVE', **msg)


@register()
class Aliens(Response):

    def reply(self, msg):
        text = msg.get('text', '')
        if 'alien' in text.lower():
            self.react('alien', **msg)
            self.react('telescope', **msg)
