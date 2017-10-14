import pytest

from scully.interfaces import Interface


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
