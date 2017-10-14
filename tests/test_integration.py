from unittest.mock import MagicMock, patch

import scully
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


def test_scully_is_a_broker(slack):
    msg = {'text': 'hows the weather?', 'channel': 'foo'}
    symbol = MagicMock()
    bot = Scully(client=slack)
    bot.slack_client.rtm_read.return_value = [msg]

    with patch('scully.interfaces.Share') as share:
        share.return_value = symbol
        symbol.get_price.return_value = 10.0
        symbol.get_days_high.return_value = 512.0
        symbol.get_days_low.return_value = 0.001
        symbol.get_prev_close.return_value = 9.75
        bot.listen()
        assert bot.slack_client.api_not_called()
        bot.slack_client.rtm_read.return_value = [{'text': '$ stock GAINS', 'channel': 'money'}]
        bot.listen()
        assert bot.slack_client.api_called_with('chat.postMessage', channel='money')
        assert bot.slack_client.api_called_with('reactions.add',
                                            name='chart_with_upwards_trend')
