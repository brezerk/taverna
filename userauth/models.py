# -*- coding: utf-8 -*-
# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, editable = False)
    openid_hash = models.CharField(editable = False, blank = True, null = True, max_length = 129)
    visible_name = models.SlugField(blank = False, null = True, max_length = 33)
    karma = models.IntegerField(default = 10)
    jabber = models.EmailField(blank = True, null = True, max_length = 32)
    website = models.CharField(blank = True, null = True, max_length = 32)
    location = models.CharField(blank = True, null = True, max_length = 32)
    sign = models.TextField(blank = True, null = True, max_length = 256)
    photo = models.CharField(blank = True, null = True, max_length = 33)

    def __unicode__(self):
        return self.user.username

    def can_create_forum(self):
        return self.karma > 15

    def can_create_topic(self):
        return self.karma > 10

    def can_create_comment(self):
        return self.karma > 1

    def get_visible_name(self):
        if self.visible_name:
            return self.visible_name
        else:
            return self.user.username
