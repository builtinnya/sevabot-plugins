#!/sevabot
# -*- coding: utf-8 -*-

"""

    URI handler module, processes URIs in Skype chat messages.

    This module needs `settings.py` in the same directory.

    Features:

        - Bookmark the URIs using Hatena Bookmark (http://b.hatena.ne.jp/) API.

        - Notify wisely if URIs in messages have already been posted.

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
import random
import re
import requests
import bs4
from HTMLParser import HTMLParseError
from requests.exceptions import RequestException
from requests_oauthlib import OAuth1

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode, get_chat_id

logger = logging.getLogger('URI')

# Set to debug only during dev
logger.setLevel(logging.INFO)

logger.debug('URI module level load import')


class URIHistory:
    """
    URI history class.
    """

    def __init__(self, history_limit_per_chat):

        logger.debug('URIHistory init (limit per chat: {})'.format(
            history_limit_per_chat
        ))

        self.histories = {}
        self.history_limit = history_limit_per_chat

        if self.history_limit < 0:
            self.history_limit = 0

    def _get_uri_and_title(self, uri):
        """
        Get the true URI and the page title.
        """

        try:
            r = requests.get(uri)
            r.raise_for_status()

            soup = bs4.BeautifulSoup(
                r.content,
                'html.parser',
                parse_only=bs4.SoupStrainer('title')
            )

            title = (soup.title and soup.title.string) or ''

            return r.url, title.strip()

        except (RequestException, HTMLParseError):
            return None, None

    def _match(self, item, msg, uri):
        """
        Whether the item matches the message.

        An item matches only if the message does not contain other than the
        URI and title.
        """

        body = ensure_unicode(msg.Body)

        title = item['title']

        remainder = body.replace(title, '').replace(uri, '').strip()

        logger.debug('Matching remainder: {}'.format(remainder))

        # Does it look like a scrap?
        return re.match(
            '^["#\'()\-=~^|\[\]{}@`;:*,.<>_\s]{0,10}$', remainder
        )

    def _add(self, history, true_uri, title, msg):
        """
        Add an item to the history.
        """

        if true_uri in history:
            return

        history[true_uri] = {
            'uri': true_uri, 'title': title, 'time': msg.Datetime
        }

        if len(history) > self.history_limit:
            history.popitem(last=False)

    def find_and_add(self, msg, uri):
        """
        Find and add a history item.
        """

        true_uri, title = self._get_uri_and_title(uri)

        logger.debug('Got {} (title: {})'.format(true_uri, title))

        if not true_uri:
            return

        chat_id = get_chat_id(msg.Chat)

        history = self.histories.get(chat_id)
        if not history:
            history = utils.LastUpdatedOrderedDict()
            self.histories[chat_id] = history

        item = history.get(true_uri)
        if not item:
            self._add(history, true_uri, title, msg)
            return

        return self._match(item, msg, uri) and item


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

        self.enable_notification = settings.URI_ENABLE_NOTIFICATION
        self.notification_formats = settings.URI_NOTIFICATION_FORMATS
        self.history = URIHistory(settings.URI_HISTORY_LIMIT_PER_CHAT)

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

    def notify_already_posted(self, uri, msg):
        """
        Notify wisely that the URI has already been posted in the chat.
        """

        def extend_history_item(item):
            """
            Extend a history item for valuable information.
            """

            duration = msg.Datetime - item['time']

            item['timedelta_ja'] = utils.timedelta_in_japanese(duration)

        if not self.enable_notification:
            return

        item = self.history.find_and_add(msg, uri)
        if item:
            logger.debug('History item found: {}'.format(item))
            extend_history_item(item)
            notification_format = random.choice(self.notification_formats)
            msg.Chat.SendMessage(notification_format.format(**item))

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        body = ensure_unicode(msg.Body)

        logger.debug('URI handler got: {}'.format(body))

        uris = re.findall(self.uri_regexp, body)

        for uri in uris:
            self.hatena_bookmark(uri, msg)
            self.notify_already_posted(uri, msg)

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
