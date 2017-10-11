from unittest.mock import MagicMock

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
