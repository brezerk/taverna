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

from django.contrib import admin
from django.contrib.auth.models import User
from models import Profile, ReasonList

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'karma', 'jabber', 'website', 'openid')

admin.site.register(Profile, ProfileAdmin)

class ReasonAdmin(admin.ModelAdmin):
    list_display = ('description', 'cost',)

admin.site.register(ReasonList, ReasonAdmin)
