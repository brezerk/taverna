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

from taverna.blog.feeds import RssBlogTraker, AtomBlogTraker, RssBlog, AtomBlog
from taverna.blog.sitemaps import BlogSitemap
from taverna.forum.feeds import RssForum, AtomForum, RssComments, AtomComments
from taverna.userauth.feeds import RssUser, AtomUser, RssNotify, AtomNotify

admin.autodiscover()


sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns = patterns('',
    (r'^sudo/', include(admin.site.urls)),

    (r'^libthread.so.(?P<post_id>\d+).0$', 'forum.views.thread'),
    (r'^libcups.so.(?P<post_id>\d+)$', 'forum.views.print_post'),

    (r'^$', 'blog.views.index'),

    (r'^blog/libblog.so.(?P<blog_id>\d+).0$', 'blog.views.view'),
#    (r'^blog/all/libblog-(?P<user_id>\d+).so$', 'blog.views.view_all'),

    (r'^blog/libdiff-(?P<diff_id>\d+).so$', 'forum.views.post_diff'),
    (r'^blog/librollback-(?P<diff_id>\d+).so$', 'forum.views.post_rollback'),

    url(r'^librss-0.so$', RssBlogTraker(), name='rss_blog_traker'),
    url(r'^libatom-0.so$', AtomBlogTraker(), name='atom_blog_traker'),

    (r'^share/$', 'blog.views.list'),
    (r'^share/local/$', 'blog.views.list_public'),
    (r'^share/usr/$', 'blog.views.list_users'),
    (r'^blog/libpost-new.so$', 'blog.views.post_add'),
    (r'^blog/libpost-edit-(?P<post_id>\d+).so$', 'blog.views.post_edit'),
    (r'^blog/libsettings.so$', 'blog.views.blog_settings'),
    (r'^blog/libtag-(?P<tag_id>\d+).so$', 'blog.views.tags_search'),

    (r'^forum/$', 'forum.views.index'),
    (r'^forum/libforum.so.(?P<forum_id>\d+).0$', 'forum.views.forum'),

    url(r'^forum/librss-(?P<forum_id>\d+).so$', RssForum(), name='rss_forum_traker'),
    url(r'^forum/libatom-(?P<forum_id>\d+).so$', AtomForum(), name='atom_forum_traker'),

    (r'^forum/posting.so$', 'forum.views.reply'),
    (r'^libreply.so.(?P<post_id>\d+)$', 'forum.views.reply'),

    url(r'^thread/librss-(?P<post_id>\d+).so$', RssComments(), name='rss_comments'),
    url(r'^thread/libatom-(?P<post_id>\d+).so$', AtomComments(), name='atom_comments'),

    (r'^forum/createtopic.(?P<forum_id>\d+).so$', 'forum.views.topic_create'),
    (r'^forum/edittopic.(?P<topic_id>\d+).so$', 'forum.views.topic_edit'),
    (r'^forum/createforum.so$', 'forum.views.forum_create'),
    (r'^forum/libtag-(?P<tag_id>\d+).so$', 'forum.views.tags_search'),
    (r'^forum/traker.so$', 'forum.views.traker'),

    (r'^liboffset-(?P<root_id>\d+).so.(?P<offset_id>\d+)$', 'forum.views.offset'),
    (r'^libremove-(?P<post_id>\d+).so$', 'forum.views.remove'),
    (r'^libview-(?P<post_id>\d+).so$', 'forum.views.post_view'),
    (r'^libsolve-(?P<post_id>\d+).so$', 'forum.views.post_solve'),

    (r'^pam/liblogout.so$', 'userauth.views.openid_logout'),
    (r'^pam/libprofile-(?P<user_id>\d+).so$', 'userauth.views.profile_view'),
    (r'^~$', 'userauth.views.profile_view'),
    (r'^pam/libprofile-edit.so$', 'userauth.views.profile_edit'),
    (r'^pam/libcomments-(?P<user_id>\d+).so$', 'userauth.views.user_comments'),
    (r'^pam/libnotify.so$', 'userauth.views.notify'),

    url(r'^pam/notify/librss-(?P<user_id>\d+).so$', RssNotify(), name='rss_notify'),
    url(r'^pam/notify/libatom-(?P<user_id>\d+).so$', AtomNotify(), name='atom_notify'),

    (r'^pam/librewards-(?P<user_id>\d+).so$', 'userauth.views.rewards'),
    (r'^pam/libgraweyard.so$', 'userauth.views.graveyard'),
    (r'^index.php$', 'blog.views.firebox'),

    (r'^libajax-(?P<post_id>\d+)-(?P<positive>\d+).so$', 'blog.views.vote_async'),
    (r'^blog/libvote-(?P<post_id>\d+)-(?P<positive>\d+).so$', 'blog.views.vote_generic'),

    url(r'^pam/librss-(?P<user_id>\d+).so$', RssUser(), name='rss_user'),
    url(r'^pam/libatom-(?P<user_id>\d+).so$', AtomUser(), name='atom_user'),

    (r'^login/$', 'userauth.views.openid_chalange'),
    (r'^login/finish/$', 'userauth.views.openid_finish'),

    url(r'^blog/librss-(?P<blog_id>\d+).so$', RssBlog(), name='rss_blog'),
    url(r'^blog/libatom-(?P<blog_id>\d+).so$', AtomBlog(), name='atom_blog'),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login/"
