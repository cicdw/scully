import logging


class Post(object):

    user = 'U7G9A6Y7R'
    AT = '<@U7G9A6Y7R>'

    @property
    def __name__(self):
        return type(self).__name__

    def say(self, words, channel=None, **kwargs):
        logging.info('{0} saying "{1}" in channel {2}'.format(self.__name__, words, channel))
        posted_msg = self.slack_client.api_call("chat.postMessage",
                                    channel=channel,
                                    text=words,
                                    as_user=True)
        return posted_msg

    def react(self, emoji, channel=None, ts=None, **kwargs):
        logging.info('{0} reacting with :{1}: in channel {2}'.format(self.__name__, emoji, channel))
        posted_msg = self.slack_client.api_call("reactions.add",
                                    channel=channel,
                                    name=emoji,
                                    timestamp=ts, as_user=True)
        return posted_msg

    def __init__(self, slack_client):
        self.slack_client = slack_client
