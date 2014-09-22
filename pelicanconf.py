#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals


###############################################################################

RELATIVE_URLS = True
LOCALE = 'en_US.utf8'
SITEURL = ''
PATH = 'content'
THEME = 'themes/pure'
STATIC_PATHS = ['images', 'pdfs']
DEFAULT_CATEGORY = ''
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU  = False
DEFAULT_DATE = 'fs'
FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.*)'

ARTICLE_URL = '{slug}/'
ARTICLE_SAVE_AS = '{slug}/index.html'

PAGE_URL = '{slug}/index.html'
PAGE_SAVE_AS = '{slug}/index.html'

CATEGORY_SAVE_AS = ''
TAG_SAVE_AS = ''
TAGS_SAVE_AS = ''
AUTHOR_SAVE_AS = ''
TWITTER_USERNAME = 'cyrillerossant'
MENUITEMS = [('Home', '/'),
             ('Projects', '/projects/'),
             ('Books', '/books/'),
             ('Resume', '/resume/'),
            ]
DATE_FORMATS = {
    'en': '%Y-%m-%d',
}

###############################################################################




AUTHOR = 'Cyrille Rossant'
SITENAME = 'Cyrille Rossant'

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = ()

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10



