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
from taverna.forum.models import Post
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from taverna.parsers.templatetags.markup import markup

from django.core.paginator import Paginator

from django.conf import settings

class RssNotify(Feed):
    link = ""
    description = ""
    title = ""

    def get_object(self, request, user_id):
        return get_object_or_404(User, pk=user_id)

    def items(self, obj):
        self.title =  _("Last user \"%s\" notifyes" % (obj.profile.get_visible_name()))
        self.link = obj.get_absolute_url()
        return Post.objects.exclude(owner=obj).filter(forum = None, blog = None, reply_to__owner = obj).order_by('-created')[:settings.PAGE_LIMITATIONS["FORUM_TOPICS"]]

    def item_title(self, item):
        return "%s - %s" % (item.thread.get_section_name(), item.thread.title)

    def item_description(self, item):
        return markup(item.text, item.parser)

    def item_author_name(self, item):
        return item.owner.profile.visible_name

    def item_pubdate(self, item):
        return item.created

    def item_link(self, item):
        return reverse("forum.views.offset", args=[item.thread.pk, item.pk])

class AtomNotify(RssNotify):
    feed_type = Atom1Feed

class RssUser(Feed):
    link = ""
    description = ""
    title = ""

    def get_object(self, request, user_id):
        return get_object_or_404(User, pk=user_id)

    def items(self, obj):
        self.title =  _("Last topics of user \"%s\"" % (obj.profile.get_visible_name()))
        self.link = obj.get_absolute_url()
        return Post.objects.exclude(forum=None,blog=None).filter(owner=obj).order_by('-created')[:settings.PAGE_LIMITATIONS["BLOG_POSTS"]]

    def item_title(self, item):
        if (item.forum):
            return "%s - %s" % (item.forum.name, item.title)
        else:
            return "%s - %s" % (item.blog.name, item.title)

    def item_description(self, item):
        return markup(item.text, item.parser)

    def item_author_name(self, item):
        return item.owner.profile.visible_name

    def item_pubdate(self, item):
        return item.created

class AtomUser(RssUser):
    feed_type = Atom1Feed

