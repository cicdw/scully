import logging
import re
import sys


HELP_REGISTRY = {}
REGISTRY = []
def register(register_help=False, skip_test=False):
    def decorator(post):
        if register_help:
            HELP_REGISTRY[post.cmd] = post.cli_doc

        if skip_test and hasattr(sys, '_within_test'):
            return post
        else:
            REGISTRY.append(post)
            return post
    return decorator


class Post(object):

    user = 'U7G9A6Y7R'
    AT = '<@U7G9A6Y7R>'

    @property
    def name(self):
        return type(self).__name__

    def sanitize(self, txt):
        '''Replace curly quotes and remove things in brackets'''
        return re.sub("{.*?}", "", txt.replace('“', '"').replace('”', '"'))

    def say(self, words, channel=None, **kwargs):
        self.log.info('{0} saying "{1}" in channel {2}'.format(self.name, words, channel))
        posted_msg = self.slack_client.api_call("chat.postMessage",
                                    channel=channel,
                                    text=words,
                                    as_user=True)
        return posted_msg

    def react(self, emoji, channel=None, ts=None, **kwargs):
        txt = kwargs.get('text')
        self.log.info('{0} reacting to "{1}" with :{2}: in channel {3}'.format(self.name, txt, emoji, channel))
        posted_msg = self.slack_client.api_call("reactions.add",
                                    channel=channel,
                                    name=emoji,
                                    timestamp=ts, as_user=True)
        return posted_msg

    def __init__(self, slack_client):
        self.slack_client = slack_client
        self.log = logging.getLogger(self.name)
