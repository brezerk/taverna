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

from django.test import TestCase
from django.test.client import Client
from blog.views import *
from django.core.urlresolvers import reverse

class SimpleTest(TestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        from userauth.models import Profile
        from blog.models import Blog
        from forum.models import Post
        user = User.objects.create_user('test', 'test@example.com', 'secret')
        user.save()
        profile = Profile(user = user, visible_name = user.username)
        profile.save()
        blog = Blog(active = True, owner = user, name = "Tester's blog")
        blog.save()
        tag = Tag(name = "test tag")
        tag.save()
        post = Post(owner = user, title = "Title", text = "This is test text", blog = blog)
        post.save()
        post.tags = [tag]
        post.save()

    def testStatusCodes(self):
        client = Client()
        # Let's try to view @login_required pages with non logged in client.
        # Expecting 302 status code
        self.failUnlessEqual(client.get(reverse(blog_settings)).status_code, 302)
        self.failUnlessEqual(client.get(reverse(post_edit, args = [1])).status_code, 302)
        self.failUnlessEqual(client.get(reverse(post_add)).status_code, 302)
        # Trying to log in.
        client.login(username = "test", password = "secret")
        # Checking @login_required pages with logged in user
        self.failUnlessEqual(client.get(reverse(blog_settings)).status_code, 200)
        self.failUnlessEqual(client.get(reverse(post_edit, args = [1])).status_code, 200)
        self.failUnlessEqual(client.get(reverse(post_add)).status_code, 200)
        # Trying all other pages:
        self.failUnlessEqual(client.get(reverse(tags_search, args = [1])).status_code, 200)
        self.failUnlessEqual(client.get(reverse(view, args = [1])).status_code, 200)
        self.failUnlessEqual(client.get(reverse(index)).status_code, 200)
        self.failUnlessEqual(client.get(reverse(firebox)).status_code, 200)
        self.failUnlessEqual(client.get(reverse(list)).status_code, 200)
        self.failUnlessEqual(client.get(reverse(list_public)).status_code, 200)
        self.failUnlessEqual(client.get(reverse(list_users)).status_code, 200)
        # TODO: check ajax votes
        client.logout()
        
