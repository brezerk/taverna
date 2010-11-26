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
from models import *
from views import *
from django.test.client import Client

class SimpleForumTest(BaseTest):

    def setUp(self):
        self.setUpProfile()
        forum = Forum(name="Test Forum", description="Test", owner=self.user)
        forum.save()
        post = Post(owner=self.user, title="Test", text="Test", forum=forum)
        post.save()
        post.thread = post
        post.save()

    def testAnonymousStatusCodes(self):
        """
        Check anonymous viewable pages:
        """
        client = self.getAnonymousClient()
        self.assertEqual(client.get(reverse(index)).status_code, 200)
        for v in forum, thread, print_post:
            self.assertEqual(client.get(reverse(v, args=[1])).status_code, 200)

    def testLoggedInStatusCodes(self):
        """
        Check login required pages:
        """
        client = self.getLoggedInClient()
        self.assertEqual(client.get(reverse(forum_create)).status_code, 200)
        self.assertEqual(client.get(reverse(topic_create, args=[1])).status_code, 200)
        self.assertEqual(client.get(reverse(reply, args=[1])).status_code, 200)

