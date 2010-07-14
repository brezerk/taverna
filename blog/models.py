# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.core.urlresolvers import reverse

from django.conf import settings

class Blog(models.Model):
    name = models.SlugField(max_length = 32, unique = True)
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

