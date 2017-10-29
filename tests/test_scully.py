from unittest.mock import MagicMock
from websocket._exceptions import WebSocketConnectionClosedException as WError

from scully import Scully


def test_scully_initializes():
    bot = Scully(client=MagicMock())


def test_scully_starts():
    bot = Scully(client=MagicMock())
    bot.start(1)


def test_scully_listens():
    bot = Scully(client=MagicMock())

    class FakeResponse(object):
        def __init__(self, *args, **kwargs):
            self.called = 0
        def __call__(self, *args, **kwargs):
            self.called = 1

    resp = FakeResponse()
    bot.responses.append(resp)
    bot.listen()
    assert resp.called == 1


def test_scully_restarts_when_connection_closes():
    client = MagicMock()
    bot = Scully(client=client)
    bot.slack_client.rtm_read = MagicMock(side_effect=WError("team migration"))
    bot.connect(); bot.listen()
    assert bot.slack_client.rtm_connect.call_count == 2
