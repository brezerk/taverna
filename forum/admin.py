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
from taverna.forum.models import Forum, Post

class ForumAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'owner', 'rating')

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'blog', 'forum', 'flags')

admin.site.register(Forum, ForumAdmin)
admin.site.register(Post, PostAdmin)


