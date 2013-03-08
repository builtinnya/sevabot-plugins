#!/sevabot
# -*- coding: utf-8 -*-

"""

    URI handler module, processes URIs in Skype chat messages.

    This module needs `settings.py` in the same directory.

    Features:

        - Bookmark the URIs using Hatena Bookmark (http://b.hatena.ne.jp/) API.

"""

from __future__ import unicode_literals

import imp
import os.path

# Import utilities module in the same directory
utils = imp.load_source(
    'utils',
    os.path.join(os.path.dirname(__file__), 'utils.py')
)

import logging
import re
import requests
from requests.exceptions import RequestException
from requests_oauthlib import OAuth1

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode

logger = logging.getLogger('URI')

# Set to debug only during dev
logger.setLevel(logging.INFO)

logger.debug('URI module level load import')


class URIHandler(StatefulSkypeHandler):
    """
    Skype message handler class for URIs.
    """

    def __init__(self):
        """
        Use `init` method to initialize a handler.
        """

        logger.debug('URI handler constructed')

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.

        :param sevabot: Handle to Sevabot instance.
        """

        logger.debug('URI handler init')

        self.sevabot = sevabot
        self.skype = sevabot.getSkype()

        settings = utils.load_settings()

        self.uri_regexp = settings.URI_REGEXP

        self.hatena_oauth = OAuth1(
            client_key=settings.HATENA_B_CLIENT_KEY,
            client_secret=settings.HATENA_B_CLIENT_SECRET,
            resource_owner_key=settings.HATENA_B_ACCESS_TOKEN,
            resource_owner_secret=settings.HATENA_B_ACCESS_TOKEN_SECRET,
            signature_type='auth_header'
        )

        self.hatena_post_uri = settings.HATENA_B_POST_URI
        self.hatena_post_template = settings.HATENA_B_POST_TEMPLATE

    def hatena_bookmark(self, uri, msg):
        """
        Bookmark the given URI using Hatena Bookmark API.
        """

        try:
            data = self.hatena_post_template.format(uri=uri, summary='')

            r = requests.post(
                self.hatena_post_uri,
                data=data,
                auth=self.hatena_oauth
            )

            r.raise_for_status()

        except RequestException as e:
            msg.Chat.SendMessage(e)

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        body = ensure_unicode(msg.Body)

        logger.debug("URI handler got: {}".format(body))

        uris = re.findall(self.uri_regexp, body)

        for uri in uris:
            self.hatena_bookmark(uri, msg)

        # May be further processed
        return False

    def shutdown(self):
        """
        Called when the module is reloaded.
        """

        logger.debug('URI handler shutdown')


# Export the instance to Sevabot
sevabot_handler = URIHandler()

__all__ = ['sevabot_handler']
