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

from taverna.tests import BaseTest
from views import *
from django.core.urlresolvers import reverse
from blog.models import Blog
from forum.models import Post
 
class BlogTest(BaseTest):

    def setUp(self):
        self.setUpProfile()
        blog = Blog(active = True, owner = self.user, name = "Tester's blog")
        blog.save()
        tag = Tag(name = "test tag")
        tag.save()
        post = Post(owner = self.user, title = "Title", text = "This is test text", blog = blog)
        post.save()
        post.tags = [tag]
        post.save()

    def testFeeds(self):
        client = self.getAnonymousClient()

        self.assertEqual(client.get(reverse("rss_blog", args = [1])).status_code, 200)
        self.assertEqual(client.get(reverse("rss_blog_tracker")).status_code, 200)

    def testAnonymousStatusCodes(self):
        """
        Let's try to view @login_required pages with non logged in client.
        Expecting 302 status codes
        """
        client = self.getAnonymousClient()
        self.assertEqual(client.get(reverse(post_edit, args = [1])).status_code, 302)
        self.assertEqual(client.get(reverse(blog_settings)).status_code, 302)
        self.assertEqual(client.get(reverse(post_add)).status_code, 302)

    def testLoggedInStatusCodes(self):
        """
        Checking @login_required pages with logged in user
        """
        client = self.getLoggedInClient()
        self.assertEqual(client.get(reverse(post_edit, args = [1])).status_code, 200)
        self.assertEqual(client.get(reverse(blog_settings)).status_code, 200)
        self.assertEqual(client.get(reverse(post_add)).status_code, 200)

    def testGenericStatusCodes(self):
        client = self.getLoggedInClient()
        self.assertEqual(client.get(reverse(tags_search, args = [1])).status_code, 200)
        self.assertEqual(client.get(reverse(view, args = [1])).status_code, 200)
        for v in index, firebox, list, list_public, list_users:
            self.assertEqual(client.get(reverse(v)).status_code, 200)
        client.logout()
 

