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

        def api_not_called(self):
            return not self.api_call.called

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


def test_at_mentions_believes(slack):
    atmentions = AtMentions(slack)
    msg = {'text': '<@U7G9A6Y7R>', 'channel': 'foo'}
    atmentions([msg])
    assert slack.api_called_with('chat.postMessage', text='I WANT TO BELIEVE', channel='foo')


def test_at_mentions_doesnt_believe(slack):
    atmentions = AtMentions(slack)
    msg = {'text': 'none', 'channel': 'foo'}
    atmentions([msg])
    slack.api_call.assert_not_called()


def test_add_reactions_confirms(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'scully plz react to "foo" with :bar:', 'channel': 'cat'}
    add_new([msg])
    assert slack.api_called_with('chat.postMessage',
                              channel='cat',
                              text='--reaction added for "foo"--')
    assert slack.api_called_with('reactions.add', name='bar')


def test_add_reactions_reacts(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'scully, react to "foo" with :bar:', 'channel': 'cat'}
    add_new([msg])
    new_msg = {'text': 'Foo is ridiculous', 'channel': 'cat'}
    add_new([new_msg])
    assert slack.api_called_with('reactions.add', name='bar')


def test_add_reactions_ignores_empty_strings(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'scully react to "" with :emoji:'}
    add_new([msg])
    add_new([{'text': 'new msg'}])
    slack.api_call.assert_not_called()
    msg = {'text': 'scully react to "   " with :emoji:'}
    add_new([msg])
    add_new([{'text': 'new msg'}])
    slack.api_call.assert_not_called()


def test_add_reactions_ignores_things_in_brackets(slack):
    add_new = AddReaction(slack)
    msg = {'text': '''10/13/2017 12:56:19 AM INFO: {text': 'scully please react to "tennis" with :money_mouth_face:'}'''}
    add_new([msg])
    slack.api_call.assert_not_called()


def test_add_reactions_handles_curly_quotes(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'scully react to “encoding” with :-1:'}
    add_new([msg])
    assert slack.api_called_with('chat.postMessage', text='--reaction added for "encoding"--')
    assert slack.api_called_with('reactions.add', name='-1')


def test_add_reactions_is_case_insensitive(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'Hey Scully will you react to "FoO" with :bar:', 'channel': 'cat'}
    add_new([msg])
    assert slack.api_called_with('chat.postMessage', text='--reaction added for "FoO"--',
                              channel='cat')
    assert slack.api_called_with('reactions.add', name='bar')
    add_new([{'text': 'foo me bro'}])
    assert slack.api_called_with('reactions.add', name='bar')
