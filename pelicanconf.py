#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

SITEURL = 'http://localhost:8000'

AUTHOR = 'Cyrille Rossant'
SITENAME = "Cyrille Rossant's blog"
LOCALE = 'en_US.utf8'
PATH = 'content'
THEME = 'themes/pure'
STATIC_PATHS = ['images', 'pdfs']
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU  = False
DEFAULT_DATE = 'fs'
FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.*)'

DEFAULT_PAGINATION = 10
PAGINATION_PATTERNS = (
    (1, '{base_name}/', '{base_name}/index.html'),
    (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
)

PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = [
			'render_math',
			'summary', 
			'neighbors', 
			# 'clean_summary',
]

DEFAULT_CATEGORY = ''

DIRECT_TEMPLATES = ('index', 'archives')

ARTICLE_URL = '{slug}/'
ARTICLE_SAVE_AS = '{slug}/index.html'

PAGE_URL = '{slug}/index.html'
PAGE_SAVE_AS = '{slug}/index.html'

TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = 'tag/{slug}/index.html'
TAGS_SAVE_AS = ''

AUTHOR_URL = ''
AUTHOR_SAVE_AS = ''

CATEGORY_URL = ''
CATEGORY_SAVE_AS = ''




TWITTER_USERNAME = 'cyrillerossant'
MENUITEMS = [('Home', '/'),
             ('Projects', '/projects/'),
             ('Books', '/books/'),
             ('Resume', '/resume/'),
            ]
DATE_FORMATS = {
    'en': '%Y-%m-%d',
}


PATH = 'content'
TIMEZONE = 'Europe/Paris'
DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
