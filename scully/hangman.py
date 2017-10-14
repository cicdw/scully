import logging
import os
import re
from .core import register
from .interfaces import Interface


class Hangman(Interface):

    cmd = 'hangman'
    cli_doc = '$ hangman "word or phrase" starts a new hangman game!'
    in_play = False

    def start_game(self, *args, msg=None):
        word = re.compile('".+"').search(args[0])
        if not word:
            self.say('```invalid starting word {} provided.```'.format(args[0]), **msg)
            return
        else:
            word = self.sanitize(word.group()).replace('"', '')

        self.say('```hangman game begun with word "{}"```'.format(word), **msg)

    def interface(self, *args, msg=None):
        if not self.in_play:
            self.start_game(*args, msg=msg)
