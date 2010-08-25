# -*- coding: utf-8 -*-
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

    def get_visible_name(self):
        if self.visible_name:
            return self.visible_name
        else:
            return "User-%i" % self.id

