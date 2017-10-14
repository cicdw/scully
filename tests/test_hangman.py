from scully.hangman import Hangman


def test_hangman_starts(slack):
    game = Hangman(slack)
    game([{'text': '$ hangman new "word"', "channel": 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```hangman game begun with word "word"```')


def test_hangman_doesnt_break_on_bad_calls(slack):
    game = Hangman(slack)
    game([{'text': '$ hangman new word', "channel": 'game'}])
    assert game.slack_client.api_called_with('chat.postMessage',
                                 text='```invalid starting word word provided.```',
                                 channel='game')


def test_hangman_displays_status(slack):
    game = Hangman(slack)
    game([{'text': '$ hangman new "word"', "channel": 'game'}])
    game([{'text': '$ hangman', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ _```')


def test_hangman_displays_status_after_guess(slack):
    game = Hangman(slack)
    game([{'text': '$ hangman new "word"', "channel": 'game'}])
    game([{'text': '$ hangman', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ _```')
    game([{'text': '$ hangman "d"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ d```')


def test_hangman_doesnt_break_with_bad_guess(slack):
    game = Hangman(slack)
    game([{'text': '$ hangman new "word"', "channel": 'game'}])
    game([{'text': '$ hangman', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ _```')
    game([{'text': '$ hangman d', 'channel': 'game'}])
    game([{'text': '$ hangman', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ _```')


def test_hangman_correctly_handles_sequential_guesses(slack):
    game = Hangman(slack)
    game([{'text': '$ hangman new "word"', "channel": 'game'}])
    game([{'text': '$ hangman', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ _```')
    game([{'text': '$ hangman "d"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ d```')
    game([{'text': '$ hangman "e"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ d```')
    game([{'text': '$ hangman "o"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ o _ d```')
    game([{'text': '$ hangman "w"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```w o _ d```')
    game([{'text': '$ hangman "l"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```w o _ d```')


def test_hangman_correctly_ends_game(slack):
    game = Hangman(slack)
    game([{'text': '$ hangman new "word"', "channel": 'game'}])
    game([{'text': '$ hangman', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ _```')
    game([{'text': '$ hangman "d"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ _ _ d```')
    game([{'text': '$ hangman "o"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```_ o _ d```')
    game([{'text': '$ hangman "w"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```w o _ d```')
    game([{'text': '$ hangman "r"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```w o r d```')
    assert slack.api_called_with('chat.postMessage',
                                 text='```You win!```')
    game([{'text': '$ hangman', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```---no game in progress---```')


def test_scully_supports_winners(slack):
    game = Hangman(slack)
    game([{"text": '$ hangman new "e"', "channel": 'game'}])
    game([{'text': '$ hangman "e"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```e```')
    assert slack.api_called_with('chat.postMessage',
                                 text='```You win!```')
    assert slack.api_called_with('reactions.add',
                                 name='100')


def test_scully_allows_for_user_defined_guesses(slack):
    game = Hangman(slack)
    game([{"text": '$ hangman new "word" 1', "channel": 'game'}])
    game([{'text': '$ hangman "q"', 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```Game lost! The word was "{}"```'.format("word"))
    assert slack.api_called_with('reactions.add', name='skull')
    game([{'text': '$ hangman'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```---no game in progress---```')


def test_scully_stops_after_ten_guesses_by_default(slack):
    game = Hangman(slack)
    game([{"text": '$ hangman new "word"', "channel": 'game'}])
    for letter in 'qetyuipasf':
        game([{'text': '$ hangman "{}"'.format(letter), 'channel': 'game'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```Game lost! The word was "{}"```'.format("word"))
    assert slack.api_called_with('reactions.add', name='skull')
    game([{'text': '$ hangman'}])
    assert slack.api_called_with('chat.postMessage',
                                 text='```---no game in progress---```')
