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

from django.conf.urls.defaults import *
from django.conf import settings
from django.core.urlresolvers import reverse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from taverna.blog.sitemaps import BlogSitemap
from taverna.forum.feeds import RssForum, AtomForum, RssComments, AtomComments
from taverna.userauth.feeds import RssUser, AtomUser, RssNotify, AtomNotify

admin.autodiscover()


sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns = patterns('',
    (r'^sudo/', include(admin.site.urls)),

    (r'^lib/thread.so.(?P<post_id>\d+)$', 'forum.views.thread'),
    (r'^lib/cups.so.(?P<post_id>\d+)$', 'forum.views.print_post'),

    (r'^$', 'blog.views.index'),

    (r'^share/libblog.so.(?P<blog_id>\d+)$', 'blog.views.view'),
#    (r'^blog/all/libblog-(?P<user_id>\d+).so$', 'blog.views.view_all'),

    (r'^lib/diff.so.(?P<diff_id>\d+)$', 'forum.views.post_diff'),
    (r'^lib/rollback.so.(?P<diff_id>\d+)$', 'forum.views.post_rollback'),

    (r'^share/$', 'blog.views.list'),
    (r'^share/local/$', 'blog.views.list_public'),
    (r'^share/usr/$', 'blog.views.list_users'),
    (r'^bin/vim$', 'blog.views.post_add'),
    (r'^share/libvim.so.0.(?P<post_id>\d+)$', 'blog.views.post_edit'),
    (r'^blog/libsettings.so$', 'blog.views.blog_settings'),
    (r'^sahre/libtag.so.(?P<tag_id>\d+)$', 'blog.views.tags_search'),

    (r'^forum/$', 'forum.views.index'),
    (r'^forum/libforum.so.(?P<forum_id>\d+)$', 'forum.views.forum'),

    url(r'^lib/forum/librss.so.(?P<forum_id>\d+)$', RssForum(), name='rss_forum_traker'),
    url(r'^lib/forum/libatom.so.(?P<forum_id>\d+)$', AtomForum(), name='atom_forum_traker'),

    (r'^lib/reply.so.(?P<post_id>\d+)$', 'forum.views.reply'),

    url(r'^lib/thread/librss.so.(?P<post_id>\d+)$', RssComments(), name='rss_comments'),
    url(r'^lib/thread/libatom.so.(?P<post_id>\d+)$', AtomComments(), name='atom_comments'),

    (r'^forum/libvim.so.0.(?P<forum_id>\d+)$', 'forum.views.topic_create'),
    (r'^forum/libvim.so.1.(?P<topic_id>\d+)$', 'forum.views.topic_edit'),
    (r'^bin/mkdir$', 'forum.views.forum_create'),
    (r'^forum/libtag.so.(?P<tag_id>\d+)$', 'forum.views.tags_search'),
    (r'^forum/traker.so$', 'forum.views.traker'),

    (r'^lib/offset.so.(?P<root_id>\d+).(?P<offset_id>\d+)$', 'forum.views.offset'),
    (r'^sbin/remove.so.(?P<post_id>\d+)$', 'forum.views.remove'),
#    (r'^libview-(?P<post_id>\d+).so$', 'forum.views.post_view'),
    (r'^lib/libsolve.so.(?P<post_id>\d+)$', 'forum.views.post_solve'),

    (r'^lib/pam_logout.so$', 'userauth.views.openid_logout'),
    (r'^lib/pam_access.so.(?P<user_id>\d+)$', 'userauth.views.profile_view'),
    (r'^~$', 'userauth.views.profile_view'),
    (r'^lib/pam_env.so$', 'userauth.views.profile_edit'),
    (r'^lib/pam_comments.so.(?P<user_id>\d+)$', 'userauth.views.user_comments'),
    (r'^lib/libnotify.so$', 'userauth.views.notify'),

    url(r'^lib/notify/librss.so.(?P<user_id>\d+)$', RssNotify(), name='rss_notify'),
    url(r'^lib/notify/libatom.so.(?P<user_id>\d+)$', AtomNotify(), name='atom_notify'),

    (r'^pam/librewards-(?P<user_id>\d+).so$', 'userauth.views.rewards'),
    (r'^dev/graveyard$', 'userauth.views.graveyard'),
    (r'^index.php$', 'blog.views.firebox'),

    (r'^lib/ajax.so.(?P<post_id>\d+).(?P<positive>\d+)$', 'blog.views.vote_async'),
    (r'^lib/libvote.so.(?P<post_id>\d+).(?P<positive>\d+)$', 'blog.views.vote_generic'),

    url(r'^lib/pam/librss.so.(?P<user_id>\d+)$', RssUser(), name='rss_user'),
    url(r'^lib/pam/libatom.so.(?P<user_id>\d+)$', AtomUser(), name='atom_user'),

    (r'^login/$', 'userauth.views.openid_chalange'),
    (r'^login/finish/$', 'userauth.views.openid_finish'),

    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login/"
