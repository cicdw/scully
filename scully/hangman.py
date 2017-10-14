import logging
import os
import re
from .core import register
from .interfaces import Interface


@register(register_help=True)
class Hangman(Interface):

    cmd = 'hangman'
    cli_doc = '''$ hangman new "word" starts a new hangman game!
    $ hangman "*" guesses a single letter
    $ hangman --empty-- displays the current game status
    $ hangman kill terminates the current game
'''


    def __init__(self, *args, **kwargs):
        self.in_play = False
        self.guesses = []
        self.max_guesses = 10
        super().__init__(*args, **kwargs)

    def start_game(self, *args, msg=None):
        if len(args) == 0:
            self.print_status(msg=msg)
            return
        elif self.in_play:
            self.say('Game already in progress! use `$ hangman kill` to end it.', **msg)
            return

        word = re.compile('".+"').search(args[0])
        if not word or ' ' in args[0]:
            self.say('```invalid starting word {} provided.```'.format(args[0]), **msg)
            return
        else:
            word = self.sanitize(word.group()).replace('"', '')

        try:
            self.max_guesses = int(args[1])
        except:
            self.max_guesses = 10

        self.in_play = True
        self.word = list(zip(word, '_' * len(word)))
        self.say('```hangman game begun with word "{}"```'.format(word), **msg)

    def print_status(self, msg=None):
        if not self.in_play:
            self.say('```---no game in progress---```', **msg)
            return
        status = ' '.join([t[1] for t in self.word])
        self.say('```' + status + '```', **msg)

    def is_won(self):
        if len([g for _, g in self.word if g == '_']) == 0:
            return True
        else:
            return False

    def guess(self, c, msg=None):
        guess = re.compile('".+"').search(c)
        if not guess:
            self.say('```invalid guess {} provided.```'.format(c), **msg)
            return

        guess = self.sanitize(guess.group()).replace('"', '')
        if (len(guess) != 1):
            self.say('```invalid guess {} provided.```'.format(c), **msg)
            return
        if guess in self.guesses:
            self.say('```already guessed {}!```'.format(guess), **msg)
            return

        self.word = self._update_letters(guess)
        if len(self.guesses) == self.max_guesses:
            ans = ''.join([w for w, _ in self.word])
            loser_msg = self.say('```Game lost! The word was "{}"```'.format(ans), **msg)
            self.react('skull', **loser_msg)
            self.clear_game()
            return

        self.print_status(msg=msg)
        if self.is_won():
            success_msg = self.say('```You win!```', **msg)
            self.react('100', **success_msg)
            self.clear_game()

    def clear_game(self):
        self.in_play = False
        self.guesses = []
        del self.word

    def _update_letters(self, guess):
        out = [(w, t.replace('_', guess) if w == guess else t) for w, t in self.word]
        self.guesses.append(guess)
        return out

    def interface(self, *args, msg=None):
        if len(args) == 0:
            self.print_status(msg=msg)
        elif args[0] == 'new':
            self.start_game(*args[1:], msg=msg)
        elif args[0] == 'kill':
            self.clear_game()
            self.print_status(msg=msg)
        else:
            self.guess(args[0], msg=msg)
