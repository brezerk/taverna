# -*- coding: utf-8 -*-
# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    karma = models.IntegerField(null=True, default=0)
    jabber = models.CharField(null=True, max_length=32)
    website = models.CharField(null=True, max_length=32)
    location = models.CharField(null=True, max_length=32)
    sign = models.CharField(null=True, max_length=256)
    photo = models.CharField(null=True, max_length=33)

    def __unicode__(self):
        return self.user.username