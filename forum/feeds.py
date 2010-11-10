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

from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from taverna.forum.models import Forum, Post
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from taverna.parsers.templatetags.markup import markup
from django.conf import settings

from django.core.paginator import Paginator
from cache import CacheManager

class RssForum(Feed):
    link = ""
    description = ""
    title = ""

    def get_object(self, request, forum_id):
        manager = CacheManager()
        forum = manager.request_cache("forum.%s" % (forum_id), Forum.objects.get(pk = forum_id))
        return forum

    def items(self, obj):
        self.title = _("Last topics in form: %s" % (obj.name))
        self.description = obj.description
        self.link = obj.get_absolute_url()

        manager = CacheManager()
        topics = manager.request_cache('posts.forum.%s' % (obj.pk),
                 Post.objects.filter(reply_to = None, forum = obj, removed = False).order_by('-sticked', '-created'))

        return topics[:settings.PAGE_LIMITATIONS["FORUM_TOPICS"]]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markup(item.text, item.parser)

class AtomForum(RssForum):
    feed_type = Atom1Feed
    subtitle = RssForum.description


class RssComments(Feed):
    link = ""
    description = ""
    title = ""

    paginator = None

    def get_object(self, request, post_id):
        manager = CacheManager()
        startpost = manager.request_cache("posts.%s" % (post_id), Post.objects.get(pk = post_id))
        return startpost

    def items(self, obj):
        self.title = obj.title
        self.description = markup(obj.text, obj.parser)

        manager = CacheManager()
        thread_list = manager.request_cache('posts.%s.comments.all.reverse' % (obj.pk),
                      Post.objects.filter(thread = obj.thread).exclude(pk = obj.pk, removed = True).order_by('-created'))

        self.paginator = Paginator(thread_list, settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])
        return thread_list[:settings.PAGE_LIMITATIONS["FORUM_COMMENTS"]]

    def item_title(self, item):
        if item.title:
            return item.title
        else:
            return item.thread.title

    def item_description(self, item):
        return item.text

    def item_link(self, item):
        for page in self.paginator.page_range:
            if item in self.paginator.page(page).object_list:
                return "%s?offset=%s#post_%s" % (reverse("forum.views.thread", args=[item.thread.pk]), page, item.pk)

        return reverse("blog.views.view", args=[item.blog.pk])

class AtomComments(RssComments):
    feed_type = Atom1Feed
    subtitle = RssComments.description

