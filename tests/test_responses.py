from unittest.mock import MagicMock

from scully.responses import AtMentions, Response


def test_response_objects_reply_when_called():
    class TestResponse(Response):
        def reply(self, msg):
            self.called = True

    resp = TestResponse(MagicMock())
    resp(['msgs'])
    assert resp.called is True


def test_at_mentions_believes():
    sc = MagicMock()
    atmentions = AtMentions(sc)
    msg = {'text': '<@U7G9A6Y7R>', 'channel': 'foo'}
    atmentions([msg])
    args, kwargs = sc.api_call.call_args

    # hopefully prevents too granular of testing...
    assert args == ('chat.postMessage',)
    assert kwargs['text'] == 'I WANT TO BELIEVE'
    assert kwargs['channel'] == 'foo'


def test_at_mentions_doesnt_believe():
    sc = MagicMock()
    atmentions = AtMentions(sc)
    msg = {'text': 'none', 'channel': 'foo'}
    atmentions([msg])
    sc.api_call.assert_not_called()
