import pytest
from unittest.mock import MagicMock, patch

import scully
from scully.interfaces import GetTickerPrice, Help, Interface
from scully.responses import AddReaction


@pytest.fixture
def test_interface():
    class TestInterface(Interface):
        cmd = 'test'
        def interface(self, *args, msg=None):
            if len(args) == 0:
                self.say('nothing', **msg)
            else:
                self.say(args[0], **msg)
    return TestInterface


def test_interface_objects_listen_for_prompt(slack, test_interface):
    resp = test_interface(slack)
    resp([{'text': 'random msg'}, {'text': 'test testing'}])
    assert slack.api_not_called()
    resp([{'text': '$ test'}])
    assert slack.api_called_with('chat.postMessage', text='nothing')
    resp([{'text': '$ test interface'}])
    assert slack.api_called_with('chat.postMessage', text='interface')


def test_get_stock_ticker_does_the_thing(slack):
    broker = GetTickerPrice(slack)
    symbol = MagicMock()
    with patch('scully.interfaces.Share') as share:
        share.return_value = symbol
        symbol.get_price.return_value = 10.0
        symbol.get_days_high.return_value = 512.0
        symbol.get_days_low.return_value = 0.001
        symbol.get_prev_close.return_value = 9.75
        broker([{'text': 'just chatting about the weather'}])
        assert broker.slack_client.api_not_called()
        broker([{'text': '$ stock SPY', 'channel': 'money'}])
        assert broker.slack_client.api_called_with('chat.postMessage', channel='money')
        assert broker.slack_client.api_called_with('reactions.add',
                                            name='chart_with_upwards_trend')


def test_help_menu_works_with_multiple_requests(slack):
    helper = Help(slack)
    helper([{'text': '$ help stock NOTHING', 'channel': 'private'}])
    expected = '```{}\n'.format(GetTickerPrice.cli_doc)
    expected += 'no help available for NOTHING```'
    assert helper.slack_client.api_called_with('chat.postMessage',
                                               text=expected, channel='private')


def test_help_menu_works_with_bad_request(slack):
    helper = Help(slack)
    helper([{'text': '$ help NOTHING', 'channel': 'private'}])
    expected = '```no help available for NOTHING```'
    assert helper.slack_client.api_called_with('chat.postMessage',
                                               text=expected, channel='private')


def test_help_menu_works_with_stocks(slack):
    helper = Help(slack)
    helper([{'text': 'just chatting away', 'channel': 'main'}])
    assert helper.slack_client.api_not_called()
    helper([{'text': '$ help stock', 'channel': 'private'}])
    expected = '```{}```'.format(GetTickerPrice.cli_doc)
    assert helper.slack_client.api_called_with('chat.postMessage',
                                               text=expected, channel='private')


def test_add_reactions_reacts(slack):
    add_new = AddReaction(slack)
    msg = {'text': '$ react "foo" :bar:', 'channel': 'private'}
    add_new([msg])
    new_msg = {'text': 'Foo is ridiculous', 'channel': 'cat'}
    add_new([new_msg])
    assert slack.api_called_with('reactions.add', name='bar', channel='cat')
