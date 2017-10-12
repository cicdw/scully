import re


class Response(object):

    def reply(self, msg):
        raise NotImplementedError

    def say(self, words, channel=None, **kwargs):
        posted_msg = self.slack_client.api_call("chat.postMessage",
                                    channel=channel,
                                    text=words,
                                    as_user=True)
        return posted_msg

    def react(self, msg, emoji):
        pass

    def __init__(self, slack_client):
        self.slack_client = slack_client

    def _reply(self, stream):
        if stream:
            for msg in stream:
                self.reply(msg)

    def __call__(self, stream):
        self._reply(stream)


class AddReaction(Response):

    _cache = {}
    call_signature = re.compile('scully.*react\sto ".*" with :.*:')
    match_string = re.compile('".*"')
    emoji_string = re.compile(':.*:')

    def add_reaction(self, text):
        listen_for = self.match_string.search(text).group().replace('"', '')
        react_with = self.emoji_string.search(text).group().replace(':', '')
        self._cache[listen_for] = react_with
        return listen_for, react_with

    def reply(self, msg):
        text = msg.get('text', '')
        reactions = [emoji for t, emoji in self._cache.items() if t.lower() in text.lower()]
        if self.call_signature.match(text):
            new_string, new_emoji = self.add_reaction(text)
            success_msg = self.slack_client.api_call("chat.postMessage",
                                        channel=msg['channel'],
                                        text='Reaction added for "{}".'.format(new_string),
                                        as_user=True)
            self.slack_client.api_call("reactions.add",
                                        channel=msg['channel'],
                                        name=new_emoji,
                                        timestamp=success_msg['ts'],
                                        as_user=True)

        if reactions:
            for emoji in reactions:
                self.slack_client.api_call("reactions.add",
                                            channel=msg['channel'],
                                            name=emoji,
                                            timestamp=msg['ts'],
                                            as_user=True)


class AtMentions(Response):

    AT = '<@U7G9A6Y7R>'

    def reply(self, msg):
        text = msg.get('text', '')
        if self.AT in text:
            self.say('I WANT TO BELIEVE', **msg)


class Aliens(Response):

    def reply(self, msg):
        text = msg.get('text', '')
        if 'alien' in text.lower():
            self.slack_client.api_call("reactions.add",
                                        channel=msg['channel'],
                                        name='alien',
                                        timestamp=msg['ts'], as_user=True)
            self.slack_client.api_call("reactions.add",
                                        channel=msg['channel'],
                                        name='telescope',
                                        timestamp=msg['ts'], as_user=True)
