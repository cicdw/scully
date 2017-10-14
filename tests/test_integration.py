from scully import Scully


def test_scully_believes(slack):
    msg = {'text': '<@U7G9A6Y7R>', 'channel': 'foo'}
    bot = Scully(client=slack)
    bot.slack_client.rtm_read.return_value = [msg]
    bot.listen()
    assert bot.slack_client.api_called_with('chat.postMessage',
                                            text='I WANT TO BELIEVE',
                                            channel='foo')


def test_scully_doesnt_believe(slack):
    msg = {'text': 'none', 'channel': 'foo'}
    slack.rtm_read.return_value = [msg]
    bot = Scully(client=slack)
    bot.listen()
    assert bot.slack_client.api_not_called()


def test_scully_aliens(slack):
    msg = {'text': 'AlIeNs', 'channel': 'foo', 'ts': None}
    bot = Scully(client=slack)
    bot.slack_client.rtm_read.return_value = [msg]
    bot.listen()
    assert bot.slack_client.api_called_with('reactions.add', name='alien', channel='foo')
    assert bot.slack_client.api_called_with('reactions.add', name='telescope', channel='foo')
