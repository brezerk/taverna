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
 
class BaseTest(TestCase):

    def setUpProfile(self):
        from django.contrib.auth.models import User
        from userauth.models import Profile
        self.user = User.objects.create_user('test', 'test@example.com', 'secret')
        self.user.save()
        self.profile = Profile(user = self.user, visible_name = self.user.username)
        self.profile.save()

    def getAnonymousClient(self):
        return Client()

    def getLoggedInClient(self):
        client = Client()
        client.login(username = "test", password = "secret")
        return client

