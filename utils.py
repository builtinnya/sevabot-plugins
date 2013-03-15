# -*- coding: utf-8 -*-

"""
    Utilities for custom modules.
"""

from __future__ import unicode_literals

import os.path
import sys
import imp
from collections import OrderedDict


class LastUpdatedOrderedDict(OrderedDict):
    """
    Store items in the order the keys were last added.
    """

    def __setitem__(self, key, value):

        if key in self:
            del self[key]

        OrderedDict.__setitem__(self, key, value)


def load_settings(name='settings', filename='settings.py', exit_on_fail=True):
    """
    (Re)load settings for custom modules.

    :param name: Used to create or access a module object.

    :param filename: Name of source file.

    :param exit_on_fail: Whether exits if the loading fails.

    :return: Settings module object.
    """

    try:
        # Load settings module in the same directory
        path = os.path.join(os.path.dirname(__file__), filename)
        settings = imp.load_source(name, path)

    except Exception:
        if exit_on_fail:
            sys.exit('Could not load settings file: {}'.format(path))
        return

    return settings


def decompose_timedelta(duration):
    """
    Decompose a duration (timedelta) object into hours, minutes, and seconds.
    """

    days, seconds = duration.days, duration.seconds
    hours = (days * 24 + seconds) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return hours, minutes, seconds


def timedelta_in_japanese(duration):
    """
    Convert a duration (timedelta) object into Japanese representation.
    """

    hms = decompose_timedelta(duration)

    result = ''
    for amount, word in zip(hms, ['時間', '分', '秒']):
        if amount > 0:
            result += '{} {} '.format(amount, word)

    if not result:
        result = '0 秒'

    # '前' means 'ago'
    result += '前'

    return result
