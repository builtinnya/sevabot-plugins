#!/sevabot
# -*- coding: utf-8 -*-

"""

    Evaluator for lightweight programming languages using LLEval.

    LLEval is available at http://colabv6.dan.co.jp/lleval.html

"""

from __future__ import unicode_literals

import logging
import re
import requests
from requests.exceptions import RequestException

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode

logger = logging.getLogger('LLEval')

# Set to debug only during dev
logger.setLevel(logging.INFO)

logger.debug('LLEval module level load import')

HELP_TEXT = """Evaluator for lightweight programming languages using LLEval.

Usage
------------------------------

#!<LANGUAGE_SPECIFIER>
<SOURCE_CODE>

LANGUAGE_SPECIFIER: Specify the language the code written in. Examples:

    py (python), py3 (python3.2), rb (ruby)

    /usr/bin/python, /usr/bin/python3.2, /usr/bin/ruby

See http://colabv6.dan.co.jp/lleval.html for details.

SOURCE_CODE: Source code text.


Example (FizzBuzz Questions)
------------------------------

#!py
def fizzbuzz(n):
    for i in range(1, n+1):
        if   i % 15 == 0: yield 'FizzBuzz'
        elif i %  5 == 0: yield 'Buzz'
        elif i %  3 == 0: yield 'Fizz'
        else:             yield i

for x in fizzbuzz(100): print x
"""


class LLEvalHandler(StatefulSkypeHandler):
    """
    Skype message handler class for the LLEval.
    """

    def __init__(self):
        """
        Use `init` method to initialize a handler.
        """

        logger.debug('LLEval handler constructed')

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.

        :param sevabot: Handle to Sevabot instance.
        """

        logger.debug('LLEval handler init')

        self.sevabot = sevabot
        self.skype = sevabot.getSkype()

    def help(self, msg):
        """
        Print help text to chat.
        """

        msg.Chat.SendMessage(HELP_TEXT)

    def lleval(self, lang, src, msg):
        """
        Evaluate the source code by making a query to LLEval.

        :param lang: Language specifier e.g. py, py3, c.

        :param src: Source code.

        :param msg: Skype message instance.
        """

        try:
            payload = {'l': lang, 's': src}
            r = requests.get('http://api.dan.co.jp/lleval.cgi', params=payload)
            r.raise_for_status()
            return r.json()

        except (RequestException, ValueError) as e:
            msg.Chat.SendMessage(e)

    def send_eval_result(self, response, msg):
        """
        Send the evaluation result to chat.
        """

        if not response:
            return

        stdout = response.get('stdout', '')
        stderr = response.get('stderr', '')

        if stdout and stderr:
            text = ''
            text += 'stdout:\n' + stdout + '\n'
            text += 'stderr:\n' + stderr
            msg.Chat.SendMessage(text)

        elif stdout:
            msg.Chat.SendMessage(stdout)

        elif stderr:
            msg.Chat.SendMessage(stderr)

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        body = ensure_unicode(msg.Body)

        logger.debug("LLEval handler got: {}".format(body))

        if not body.startswith('#!'):
            return False

        if status == 'SENT':
            # Avoid infinite loop caused by self-reproducing code
            return True

        m = re.match('#!(?P<lang>\S+)\s+(?P<src>.*)', body, re.DOTALL)

        if not m:
            self.help(msg)
            return True

        lang = m.group('lang')
        src = m.group('src')

        if lang.startswith('/'):
            # Source code contains language specifier
            lang = None
            src = m.group(0)

        r = self.lleval(lang, src, msg)

        self.send_eval_result(r, msg)

        return True

    def shutdown(self):
        """
        Called when the module is reloaded.
        """

        logger.debug('LLEval handler shutdown')


# Export the instance to Sevabot
sevabot_handler = LLEvalHandler()

__all__ = ['sevabot_handler']
