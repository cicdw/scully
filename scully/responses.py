class Response(object):

    def reply(self, msg):
        raise NotImplementedError

    def __init__(self, slack_client):
        self.slack_client = slack_client

    def _reply(self, stream):
        if stream:
            for msg in stream:
                self.reply(msg)

    def __call__(self, stream):
        self._reply(stream)


class AtMentions(Response):

    AT = '<@U7G9A6Y7R>'

    def reply(self, msg):
        text = msg.get('text', '')
        if self.AT in text:
            self.slack_client.api_call("chat.postMessage",
                                        channel=msg['channel'],
                                        text='I WANT TO BELIEVE', as_user=True)


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
