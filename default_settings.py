# -*- coding: utf-8 -*-

# Copyright (C) 2010 by Alexey S. Malakhov <brezerk@gmail.com>
#                       Opium <opium@jabber.com.ua>
#
# This file is part of Taverna
#
# Taverna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Taverna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Taverna.  If not, see <http://www.gnu.org/licenses/>.

# Django settings for taverna project.

import os
import sys
sys.path.append('libs')

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('brezerk', 'brezerk@gmail.com'),
)

MANAGERS = ADMINS

AUTH_PROFILE_MODULE = 'userauth.Profile'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'userauth.openidauth.OpenIDBackend', # if they fail the normal test
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT, 'taverna.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

if TEMPLATE_DEBUG:
    CACHE_BACKEND = 'dummy://'
else:
    CACHE_BACKEND = 'locmem://'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Kiev'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + '/media/'
STATIC_RSS_ROOT = MEDIA_ROOT

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=2&)-i_1-pb9z-d##_v-ap6urr3hg$xlnk8%h7i2(hfjz45x_w'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'taverna.urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + '/templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'forum',
    'blog',
    'userauth',
    'parsers',
)

# Debug toolbar
if DEBUG:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INTERNAL_IPS = ('127.0.0.1',)

    INSTALLED_APPS += (
        'debug_toolbar',
    )

    DEBUG_TOOLBAR_PANELS = (
        #'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        #'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.cache.CacheDebugPanel',
        #'debug_toolbar.panels.logger.LoggingPanel',
    )

    DEBUG_TOOLBAR_CONFIG = {
        'EXCLUDE_URLS': ('/admin',),
        'INTERCEPT_REDIRECTS': False,
    }

PARSER_ENGINES = (
    (0, 'Plain Text'),
    (1, 'BBCode'),
#   (2, 'Markdown'),
#   (3, 'MediaWiki'),
    (4, 'HTML'),
)

# Limit posts per page for blog, forums. etc.
# Why do not use just simple prefixed names like 'PAGE_BLOG_POSTS', 'PAGE_BLOG_COMMENTS'?
PAGE_LIMITATIONS = {
    'BLOG_POSTS': 10,
    'BLOG_COMMENTS': 10,
    'FORUM_TOPICS': 30,
    'FORUM_COMMENTS': 10,
    'RSS_POSTS': 16,
}

ugettext = lambda s: s

# Force price list
FORCE_PRICELIST = {
    'COMMENT_CREATE': {'COST': 1, 'DESC': ugettext('add new comments')},
    'TOPIC_EDIT': {'COST': 1, 'DESC': ugettext('edit topic')},
    'TOPIC_CREATE': {'COST': 10, 'DESC': ugettext('create new topic')},
    'VOTE': {'COST': 1, 'DESC': ugettext('voite')},
    'FORUM_CREATE': {'COST': 100, 'DESC': ugettext('create new forum')},
    'PROFILE_EDIT': {'COST': 1, 'DESC': ugettext('edit profile')},
    'BLOG_DESC_EDIT': {'COST': 1, 'DESC': ugettext('edit blog description')},
    'BLOG_NAME_EDIT': {'COST': 100, 'DESC': ugettext('edit blog name')},
}

# Force regeneration for autobanned users
FORCE_REGEN = {
    'RATE': 1,
    'BORDER': 1,
}

MIN_RATING = -10

START_RATING = 20
FRIDAY_BLOG = u"Пепятничный бред"

THEMES = (
    (0, 'default'),
    (1, 'lor'),
    (2, 'opennet'),
)

