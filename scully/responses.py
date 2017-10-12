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

    def react(self, emoji, channel=None, ts=None, **kwargs):
        posted_msg = self.slack_client.api_call("reactions.add",
                                    channel=channel,
                                    name=emoji,
                                    timestamp=ts, as_user=True)
        return posted_msg

    def __init__(self, slack_client):
        self.slack_client = slack_client

    def _reply(self, stream):
        if stream:
            for msg in stream:
                self.reply(msg)

    def __call__(self, stream):
        self._reply(stream)


class AddReaction(Response):

    call_signature = re.compile('scully.*react to ".*" with :.*:', re.IGNORECASE)
    match_string = re.compile('".*"')
    emoji_string = re.compile(':.*:')

    def __init__(self, slack_client):
        super().__init__(slack_client)
        self._cache = {}

    def add_reaction(self, text):
        listen_for = self.match_string.search(text).group().replace('"', '')
        react_with = self.emoji_string.search(text).group().replace(':', '')
        self._cache[listen_for] = react_with
        return listen_for, react_with

    def reply(self, msg):
        text = msg.get('text', '')
        reactions = [emoji for t, emoji in self._cache.items() if t.lower() in text.lower()]
        if self.call_signature.search(text):
            new_string, new_emoji = self.add_reaction(text)
            success_msg = self.say('Reaction added for {}'.format(new_string), **msg)
            self.react(new_emoji, **success_msg)

        if reactions:
            for emoji in reactions:
                self.react(emoji, **msg)


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
            self.react('alien', **msg)
            self.react('telescope', **msg)
