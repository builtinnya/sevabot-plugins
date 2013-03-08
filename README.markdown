# Sevabot Plugins

These are custom modules and scripts for [Sevabot], a [Skype] bot.
This is *NOT* an official repository for Sevabot plugins and is just for
my local needs and fun.
I hope this repository serves more meaningful examples for customizing Sevabot.

[Sevabot]: https://github.com/opensourcehacker/sevabot
[Skype]: http://www.skype.com/


## Installation

Before installing the plugins, make sure you have installed the latest
*development* version of [Sevabot].
To install the plugins, clone this repository and:

    $ cd /path/to/sevabot-plugins
    $ cp settings.py.example settings.py
    $ <edit settings.py>
    $ ./install.sh /path/to/sevabot/
    $ <add "custom" to `MODULE_PATHS` in /path/to/sevabot/settings.py>

Above creates `custom/` directory in Sevabot directory and
puts symbol links to the plugins and settings file in the `custom/`.
Make sure add "custom" to `MODULE_PATHS` in Sevabot's `settings.py`
(not `custom/settings.py`).

## Plugins

Here are brief descriptions of supported plugins.

### LLEval

Evaluate code written in lightweight programming languages by using
[Dan Kogai]'s [LLEval].

[Dan Kogai]: https://github.com/dankogai
[LLEval]: http://colabv6.dan.co.jp/lleval.html

For example, if you send the following to Skype chat Sevabot is currently in:

    #!py

    def bad_factorial(n):
        if n <= 0:
            return 1
        else:
            return n * bad_factorial(n - 1)

    print bad_factorial(10):

Sevabot will return `3628800` to the chat.

For more information, send `#!` to the chat and see help text.

### URI

Handle URIs in chat messages for various uses. Currently supported features are:

- Bookmark the URIs through [Hatena Bookmark] (Japanese) API.

[Hatena Bookmark]: http://b.hatena.ne.jp/

### Hone

Just a local joke. Disturb Honeshabri, a friend of mine.


## Copyright and License

Copyright (c) 2013 Naoto Yokoyama

Distributed under the MIT license.
See the LICENSE file for full details.


## Trademark Notice

The Skype name, associated trade marks and logos and the "S" logo are
trade marks of Skype or related entities.
Sevabot Plugins is an open source project and not associate of
Microsoft Corporation or Skype.
