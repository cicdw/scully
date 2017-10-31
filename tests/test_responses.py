from unittest.mock import MagicMock, patch

import scully
from scully.responses import AddReaction, AtMentions, DanielVerCheck, Response


def test_response_objects_reply_when_called():
    class TestResponse(Response):
        def reply(self, msg):
            self.called = True

    resp = TestResponse(MagicMock())
    resp(['msgs'])
    assert resp.called is True


def test_at_mentions_believes(slack):
    atmentions = AtMentions(slack)
    msg = {'text': '<@U7G9A6Y7R>', 'channel': 'foo'}
    atmentions([msg])
    assert slack.api_called_with('chat.postMessage', text='I WANT TO BELIEVE', channel='foo')


def test_at_mentions_doesnt_believe(slack):
    atmentions = AtMentions(slack)
    msg = {'text': 'none', 'channel': 'foo'}
    atmentions([msg])
    assert slack.api_not_called()


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
    msg = {'text': 'scully, react to "foo" with :bar:', 'channel': 'private'}
    add_new([msg])
    new_msg = {'text': 'Foo is ridiculous', 'channel': 'cat'}
    add_new([new_msg])
    assert slack.api_called_with('reactions.add', name='bar', channel='cat')


def test_add_reactions_ignores_nested_quotes(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'scully react to """" with :emoji:'}
    add_new([msg])
    add_new([{'text': 'new msg'}])
    assert slack.api_not_called()
    msg = {'text': 'scully react to """""" with :emoji:'}
    add_new([msg])
    add_new([{'text': 'new msg'}])
    assert slack.api_not_called()
    msg = {'text': 'scully react to ""  "" with :emoji:'}
    add_new([msg])
    add_new([{'text': 'new msg'}])
    assert slack.api_not_called()


def test_add_reactions_ignores_empty_strings(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'scully react to "" with :emoji:'}
    add_new([msg])
    add_new([{'text': 'new msg'}])
    assert slack.api_not_called()
    msg = {'text': 'scully react to "   " with :emoji:'}
    add_new([msg])
    add_new([{'text': 'new msg'}])
    assert slack.api_not_called()


def test_add_reactions_ignores_things_in_brackets(slack):
    add_new = AddReaction(slack)
    msg = {'text': '''10/13/2017 12:56:19 AM INFO: {text': 'scully please react to "tennis" with :money_mouth_face:'}'''}
    add_new([msg])
    assert slack.api_not_called()


def test_add_reactions_handles_curly_quotes(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'scully react to “encoding” with :-1:'}
    add_new([msg])
    assert slack.api_called_with('chat.postMessage', text='--reaction added for "encoding"--')
    assert slack.api_called_with('reactions.add', name='-1')


def test_add_reactions_handles_skin_tones(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'scully react to "deuces" with :v::skin-tone-3:'}
    add_new([msg])
    assert slack.api_called_with('chat.postMessage', text='--reaction added for "deuces"--')
    assert slack.api_called_with('reactions.add', name='v::skin-tone-3')


def test_add_reactions_is_case_insensitive(slack):
    add_new = AddReaction(slack)
    msg = {'text': 'Hey Scully will you react to "FoO" with :bar:', 'channel': 'cat'}
    add_new([msg])
    assert slack.api_called_with('chat.postMessage', text='--reaction added for "foo"--',
                              channel='cat')
    assert slack.api_called_with('reactions.add', name='bar')
    add_new([{'text': 'Foo me bro'}])
    assert slack.api_called_with('reactions.add', name='bar')


def test_daniel_ticker_posts_negative(slack):
    broker = DanielVerCheck(slack)
    symbol = MagicMock()
    with patch('scully.interfaces.Share') as share:
        share.return_value = symbol
        symbol.get_price.return_value = 0.0
        broker([{'text': 'just chatting about the weather'}])
        assert broker.slack_client.api_not_called()
        broker.do()
        assert broker.slack_client.api_called_with('chat.postMessage')
        assert broker.slack_client.api_called_with('reactions.add',
                                            name='chart_with_downwards_trend')


def test_daniel_ticker_posts_positive(slack):
    broker = DanielVerCheck(slack)
    symbol = MagicMock()
    with patch('scully.interfaces.Share') as share:
        share.return_value = symbol
        symbol.get_price.return_value = 10000.0
        broker([{'text': 'just chatting about the weather'}])
        assert broker.slack_client.api_not_called()
        broker.do()
        assert broker.slack_client.api_called_with('chat.postMessage')
        assert broker.slack_client.api_called_with('reactions.add',
                                            name='chart_with_upwards_trend')
