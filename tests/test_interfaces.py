import pytest
from unittest.mock import MagicMock, patch

import scully
from scully.interfaces import GetTickerPrice, Interface


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
