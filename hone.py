#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

    Disturb Honeshabri, a friend of mine.

"""

from __future__ import unicode_literals

import sys
import random

progname = 'hone'


def main(args):
    """Application entry point."""

    random.seed()

    messages = [
        'Shabri!',
        'Shabri?',
        'Shabriiiiiiiiiiiii!!',
        'ShabURYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
        'Sabori',
        'Shaburu',
        'inai',
        '(n)',
        '(puke)',
        'しゃぶり！',
        'しゃぼり！',
        '誰？'
    ]

    message = random.choice(messages).encode('utf-8')
    print message


if __name__ == '__main__':
    main(sys.argv[1:])
