# -*- coding: utf-8 -*-

"""
    Utilities for custom modules.
"""

from __future__ import unicode_literals

import os.path
import sys
import imp


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
