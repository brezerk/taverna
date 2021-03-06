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

from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from blog.models import Blog
from forum.models import Post
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from parsers.templatetags.markup import strippost
from parsers.templatetags.markup import markup
from django.core.paginator import Paginator
from django.conf import settings
from util import CachedFeed
from parsers.templatetags.markup import strippost


class RssBlogFeed(CachedFeed):
    cache_prefix = "rss-blog-feed"
    title = _("Last 10 blogs topics")
    link = "/"
    description = _("Updates on changes and additions to blogs topics.")

    def items(self):
        post_list = Post.get_rated_blog_posts()
        posts = post_list[:settings.PAGE_LIMITATIONS["BLOG_POSTS"]]
        return posts

    def item_title(self, item):
        return "%s - %s" % (item.blog.name, item.title)

    def item_description(self, item):
        return strippost(item.text, item)

    def item_author_name(self, item):
        return item.owner.profile.visible_name

    def item_pubdate(self, item):
        return item.created


class RssBlog(CachedFeed):
    cache_prefix = "rss-blog"
    link = ""
    description = ""
    title = ""

    def get_object(self, request, blog_id):
        return get_object_or_404(Blog, pk=blog_id)

    def items(self, obj):
        self.title = "%s: %s" % (_("Last topics for blog"), obj.name)
        self.description = obj.desc
        self.link = obj.get_absolute_url()
        post_list = Post.get_rated_users_blog_posts(obj)

        posts = post_list[:settings.PAGE_LIMITATIONS["BLOG_POSTS"]]
        return posts

    def item_title(self, item):
        return "%s - %s" % (item.blog.name, item.title)

    def item_description(self, item):
        return strippost(item.text, item)

    def item_author_name(self, item):
        return item.owner.profile.visible_name

    def item_pubdate(self, item):
        return item.created

