from unittest.mock import MagicMock

from scully import Scully


def test_scully_believes():
    sc = MagicMock()
    msg = {'text': '<@U7G9A6Y7R>', 'channel': 'foo'}
    bot = Scully(client=sc)
    bot.slack_client.rtm_read.return_value = [msg]
    bot.listen()
    args, kwargs = bot.slack_client.api_call.call_args
    assert args == ('chat.postMessage',)
    assert kwargs['text'] == 'I WANT TO BELIEVE'
    assert kwargs['channel'] == 'foo'


def test_scully_doesnt_believe():
    sc = MagicMock()
    msg = {'text': 'none', 'channel': 'foo'}
    sc.rtm_read.return_value = [msg]
    bot = Scully(client=sc)
    bot.listen()
    bot.slack_client.api_call.assert_not_called()
