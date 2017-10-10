from unittest.mock import MagicMock

from scully import Scully


def test_scully_initializes():
    bot = Scully(client=MagicMock())
