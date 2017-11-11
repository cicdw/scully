import pytest
from unittest.mock import MagicMock


def pytest_configure(config):
    import sys
    sys._within_test = True

def pytest_unconfigure(config):
    import sys
    del sys._within_test


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
