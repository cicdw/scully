import json
import logging
import os
import re
from yahoo_finance import Share
from .core import Post

CACHE_FILE = os.environ.get('SCULLY_EMOJI_CACHE')


class Response(Post):

    def reply(self, msg):
        raise NotImplementedError

    def sanitize(self, txt):
        '''Replace curly quotes and remove things in brackets'''
        return re.sub("{.*?}", "", txt.replace('“', '"').replace('”', '"'))

    def _reply(self, stream):
        if stream:
            for msg in stream:
                logging.info('Received {}'.format(msg))
                self.reply(msg)

    def __call__(self, stream):
        self._reply(stream)


class AddReaction(Response):

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

    def add_reaction(self, text):
        listen_for = self.match_string.search(text).group().replace('"', '').strip()
        react_with = self.emoji_string.search(text).group().replace(':', '')
        logging.info('{0}: Storing reaction {1} for pattern "{2}"'.format(self.__name__, react_with, listen_for))
        self._cache[listen_for] = react_with
        self.save()
        return listen_for, react_with

    def reply(self, msg):
        text = self.sanitize(msg.get('text', ''))
        reactions = [emoji for t, emoji in self._cache.items() if t.lower() in text.lower()]
        if self.call_signature.search(text) and not self.ignore_pattern.search(text):
            new_string, new_emoji = self.add_reaction(text)
            success_msg = self.say('--reaction added for "{}"--'.format(new_string), **msg)
            self.react(new_emoji, **success_msg)

        if reactions:
            for emoji in reactions:
                self.react(emoji, **msg)


class AtMentions(Response):

    def reply(self, msg):
        text = msg.get('text', '')
        if self.AT in text:
            self.say('I WANT TO BELIEVE', **msg)


class Aliens(Response):

    def reply(self, msg):
        text = msg.get('text', '')
        if 'alien' in text.lower():
            self.react('alien', **msg)
            self.react('telescope', **msg)
