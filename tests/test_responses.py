import pytest
from unittest.mock import MagicMock

from scully.responses import AddReaction, AtMentions, Response


@pytest.fixture
def slack():
    '''creates mock slack api with simpler testing API'''
    class Slack(MagicMock):
        def api_called_with(self, *args, **kwargs):
            '''asserts at least one call was made with the provided args
            and kwargs (kwargs may be a partial list)'''
            for call in self.api_call.call_args_list:
                agrees_with = []
                a, k = call
                agrees_with.append(args == a)
                agrees_with.extend([k.get(key) == val for key, val in kwargs.items()])
                if all(agrees_with):
                    return True
            return False

    return Slack()


def test_response_objects_reply_when_called():
    class TestResponse(Response):
        def reply(self, msg):
            self.called = True

    resp = TestResponse(MagicMock())
    resp(['msgs'])
    assert resp.called is True


def test_fixture_is_present(slack):
    atmentions = AtMentions(slack)
    msg = {'text': '<@U7G9A6Y7R>', 'channel': 'foo'}
    atmentions([msg])
    assert slack.api_called_with('chat.postMessage', text='I WANT TO BELIEVE', channel='foo')


def test_at_mentions_believes():
    sc = MagicMock()
    atmentions = AtMentions(sc)
    msg = {'text': '<@U7G9A6Y7R>', 'channel': 'foo'}
    atmentions([msg])
    assert sc.api_called_with(('chat.postMessage',), text='I WANT TO BELIEVE', channel='foo')


def test_at_mentions_doesnt_believe():
    sc = MagicMock()
    atmentions = AtMentions(sc)
    msg = {'text': 'none', 'channel': 'foo'}
    atmentions([msg])
    sc.api_call.assert_not_called()


def test_add_reactions_confirms():
    sc = MagicMock()
    add_new = AddReaction(sc)
    msg = {'text': 'scully plz react to "foo" with :bar:', 'channel': 'cat'}
    add_new([msg])
    assert sc.api_called_with(('chat.postMessage',),
                              channel='cat',
                              text='Reaction added for "foo".')
    assert sc.api_called_with(('reaction.add',), name='bar')


def test_add_reactions_reacts():
    sc = MagicMock()
    add_new = AddReaction(sc)
    msg = {'text': 'scully, react to "foo" with :bar:', 'channel': 'cat'}
    add_new([msg])
    new_msg = {'text': 'Foo is ridiculous', 'channel': 'cat'}
    add_new([new_msg])
    args, kwargs = sc.api_call.call_args_list[-1]
    assert args == ('reactions.add',)
    assert kwargs['name'] == 'bar'


def test_add_reactions_is_case_insensitive():
    sc = MagicMock()
    add_new = AddReaction(sc)
    msg = {'text': 'Hey Scully will you react to "FoO" with :bar:', 'channel': 'cat'}
    add_new([msg])
    args, kwargs = sc.api_call.call_args_list[0]
    assert args == ('chat.postMessage',)
    assert 'added' in kwargs['text'].lower()
    assert kwargs['channel'] == 'cat'
    args, kwargs = sc.api_call.call_args_list[1]
    assert args == ('reactions.add',)
    assert kwargs['name'] == 'bar'
    add_new([{'text': 'foo me bro'}])
    args, kwargs = sc.api_call.call_args_list[2]
    assert args == ('reactions.add',)
    assert kwargs['name'] == 'bar'
