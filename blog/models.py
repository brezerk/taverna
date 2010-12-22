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

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.core.urlresolvers import reverse

from django.conf import settings

from django.contrib.flatpages.models import FlatPage
from django.db.models.signals import post_save

class Blog(models.Model):
    name = models.CharField(max_length = 32, unique = True)
    desc = models.CharField(max_length = 48, default = _("Blog description"))
    active = models.BooleanField(default = False, editable = False)
    owner = models.ForeignKey(User)
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog.views.view", args = [self.pk])

class Tag(models.Model):
    name = models.CharField(max_length = 32, unique = True)
    def __unicode__(self):
        return self.name

def cache_flatpage(sender, **kwargs):
    from util import clear_template_cache
    instance = kwargs['instance']
    clear_template_cache('flatpage', instance.id)

post_save.connect(cache_flatpage, dispatch_uid="3e63ec", sender=FlatPage)

