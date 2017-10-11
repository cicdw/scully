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


def test_scully_aliens():
    sc = MagicMock()
    msg = {'text': 'AlIeNs', 'channel': 'foo', 'ts': None}
    bot = Scully(client=sc)
    bot.slack_client.rtm_read.return_value = [msg]
    bot.listen()
    call0, call1 = bot.slack_client.api_call.call_args_list
    args0, kwargs0 = call0
    args1, kwargs1 = call1
    assert args0 == ('reactions.add',)
    assert args1 == ('reactions.add',)
    assert kwargs0['name'] == 'alien'
    assert kwargs0['channel'] == 'foo'
    assert kwargs1['name'] == 'telescope'
    assert kwargs1['channel'] == 'foo'
