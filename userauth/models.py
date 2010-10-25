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

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

from django.utils.translation import gettext as _
from django.conf import settings

class ReasonList(models.Model):
    description = models.CharField(_("Description"), max_length = 128, blank = True, null = False)
    cost = models.IntegerField(default = 10)

    def __unicode__(self):
        return self.description

class Profile(models.Model):
    user = models.OneToOneField(User, editable = True)
    openid_hash = models.CharField(editable = False, blank = True, null = True, max_length = 129)
    visible_name = models.SlugField(blank = False, null = True, max_length = 33, unique = True)
    karma = models.IntegerField(default = 10)
    force = models.IntegerField(default = 10)
    buryed = models.BooleanField(default = 0, editable = True)
    buryed_reason = models.ForeignKey(ReasonList, blank = True, null = True, verbose_name=_("Ban reason"))
    jabber = models.EmailField(blank = True, null = True, max_length = 32)
    website = models.CharField(blank = True, null = True, max_length = 32)
    location = models.CharField(blank = True, null = True, max_length = 32)
    sign = models.TextField(blank = True, null = True, max_length = 256)
    photo = models.CharField(blank = True, null = True, max_length = 33)

    def __unicode__(self):
        return self.get_visible_name()

    def is_buryed(self):
        if self.buryed or self.karma < 0:
            return True
        else:
            return False

    def use_force(self, force_id):
        if self.force >= settings.FORCE_PRICELIST[force_id]["COST"]:
            self.force -= settings.FORCE_PRICELIST[force_id]["COST"]
            return True
        else:
            return False

    def can_create_forum(self):
        if self.buryed:
            return False
        return self.force >= settings.FORCE_PRICELIST["FORUM_CREATE"]["COST"]

    def can_create_topic(self):
        if self.buryed:
            return False
        return self.force >= settings.FORCE_PRICELIST["TOPIC_CREATE"]["COST"]

    def can_create_comment(self):
        if self.buryed:
            return False
        return self.force >= settings.FORCE_PRICELIST["COMMENT_CREATE"]["COST"]

    def can_vote(self):
        if self.buryed:
            return False
        return self.force >= settings.FORCE_PRICELIST["CAN_VOTE"]["COST"]

    def can_edit_topic(self):
        if self.buryed:
            return False
        return self.force >= settings.FORCE_PRICELIST["TOPIC_EDIT"]["COST"]

    def can_edit_profile(self):
        if self.buryed:
            return False
        return self.force >= settings.FORCE_PRICELIST["PROFILE_EDIT"]["COST"]

    def can_edit_blog_desc(self):
        if self.buryed:
            return False
        return self.force >= settings.FORCE_PRICELIST["BLOG_DESC_EDIT"]["COST"]

    def can_edit_blog_name(self):
        if self.buryed:
            return False
        return self.force >= settings.FORCE_PRICELIST["BLOG_NAME_EDIT"]["COST"]

    def get_visible_name(self):
        if self.visible_name:
            return self.visible_name
        else:
            return "User-%i" % self.id

