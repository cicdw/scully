import logging
import os
import re
from functools import wraps
from .core import register
from .interfaces import Interface


def requires_game(f):
    @wraps(f)
    def check_game(hman, *args, **kwargs):
        if not hman.in_play:
            hman.say('```---no game in progress---```', **kwargs['msg'])
        else:
            return f(hman, *args, **kwargs)
    return check_game


@register(register_help=True)
class Hangman(Interface):

    cmd = 'hangman'
    cli_doc = '''$ hangman new "word" [[guess_limit]] starts a new hangman game!
---> $ hangman "*" guesses a single letter or a full word
---> $ hangman guesses displays all previous guesses
---> $ hangman --empty-- displays the current game status
---> $ hangman kill terminates the current game
'''


    def __init__(self, *args, **kwargs):
        self.in_play = False
        self.guesses = []
        super().__init__(*args, **kwargs)

    def new_game(self, word, max_guesses=10):
        game_status = ('_ ' * len(word)).strip()

        def play(game_status, num_left):
            self.game_status = game_status
            self.num_left = num_left

            guess = yield
            spaced_word = ' '.join(word)
            revealed = ''.join([w if w == guess else g for g, w in zip(game_status, spaced_word)])
            num_left -= 1 if revealed == game_status else 0
            if revealed == spaced_word:
                yield True
            elif guess == word:
                yield True
            elif num_left == 0:
                yield False
            else:
                yield from play(revealed, num_left)

        return play(game_status, max_guesses)

    def start_game(self, *args, msg=None):
        if len(args) == 0:
            self.print_status(msg=msg)
            return
        elif self.in_play:
            self.say('Game already in progress! use `$ hangman kill` to end it.', **msg)
            return

        cleaned = self.sanitize(args[0])
        word = re.compile('".+"').search(cleaned)
        if not word or ' ' in cleaned:
            self.say('```invalid starting word {} provided.```'.format(args[0]), **msg)
            return
        else:
            word = word.group().replace('"', '')

        try:
            self.num_left = int(args[1])
        except:
            self.num_left = 10

        self.in_play = True
        self.word = word
        self.game = self.new_game(word, self.num_left)
        next(self.game)
        self.say('```hangman game begun with word "{}"```'.format(word), **msg)

    @requires_game
    def print_status(self, msg=None):
        guesses_left = '{} guesses left'.format(self.num_left)
        self.say('```' + self.game_status + ', ' + guesses_left + '```', **msg)

    @requires_game
    def guess(self, c, msg=None):
        c = self.sanitize(c)
        guess = re.compile('".+"').search(c)
        if not guess:
            self.say('```invalid guess {} provided.```'.format(c), **msg)
            return

        guess = self.sanitize(guess.group()).replace('"', '')
        self.guesses.append(guess)
        is_won = self.game.send(guess)
        if is_won is False:
            loser_msg = self.say('```Game lost! The word was "{}"```'.format(self.word), **msg)
            self.react('skull', **loser_msg)
            self.clear_game()
            return

        if is_won is True:
            success_msg = self.say('```You win!```', **msg)
            self.react('100', **success_msg)
            self.clear_game()
            return

        self.print_status(msg=msg)

    @requires_game
    def clear_game(self, *args, **kwargs):
        self.in_play = False
        self.guesses = []
        del self.word
        del self.game

    @requires_game
    def say_guesses(self, *args, msg=None, **kwargs):
        guess_list = '"' + '", "'.join(self.guesses) + '"'
        text = '```You have already guessed [{0}]```'.format(guess_list)
        self.say(text, **msg)

    def interface(self, *args, msg=None):
        if len(args) == 0:
            self.print_status(msg=msg)
            return

        cmds = {'new': self.start_game,
                'kill': self.clear_game,
                'guesses': self.say_guesses}

        if args[0] in cmds:
            cmds[args[0]](*args[1:], msg=msg)
        else:
            self.guess(args[0], msg=msg)
