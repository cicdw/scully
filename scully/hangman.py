import logging
import os
import re
from .core import register
from .interfaces import Interface


class Hangman(Interface):

    cmd = 'hangman'
    cli_doc = '''$ hangman "word or phrase" starts a new hangman game!
$ hangman "*" guesses a single letter
$ hangman --empty-- displays the current game status
'''
    in_play = False
    guesses = []

    def start_game(self, *args, msg=None):
        if len(args) == 0:
            self.say('no game in progress', **msg)

        word = re.compile('".+"').search(args[0])
        if not word:
            self.say('```invalid starting word {} provided.```'.format(args[0]), **msg)
            return
        else:
            word = self.sanitize(word.group()).replace('"', '')

        self.in_play = True
        self.word = list(zip(word, '_' * len(word)))
        self.say('```hangman game begun with word "{}"```'.format(word), **msg)

    def print_status(self, msg=None):
        status = ''.join([t[1] for t in self.word])
        self.say('```' + status + '```', **msg)

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

        self.word = self._update_letters(guess)
        self.print_status(msg=msg)

    def _update_letters(self, guess):
        out = [(w, t.replace('_', guess) if w == guess else t) for w, t in self.word]
        return out

    def interface(self, *args, msg=None):
        if not self.in_play:
            self.start_game(*args, msg=msg)
        if len(args) == 0:
            self.print_status(msg=msg)
        else:
            self.guess(args[0], msg=msg)

