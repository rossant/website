#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals


###############################################################################

PATH = 'content'
STATIC_PATHS = ['images', 'pdfs']
DEFAULT_CATEGORY = ''
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU  = False
DEFAULT_DATE = 'fs'
FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.*)'

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
             ('CV', '/cv/'),
            ]


###############################################################################




AUTHOR = 'Cyrille Rossant'
SITENAME = 'Cyrille Rossant'
SITEURL = ''

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

DEFAULT_PAGINATION = 1


# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True









