# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from django.conf import settings

class Blog(models.Model):
    name = models.CharField(max_length = 32)
    desc = models.CharField(max_length = 48, default = _("Blog description"))
    active = models.BooleanField(default = False, editable = False)
    owner = models.ForeignKey(User, editable = False)
    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length = 32, unique = True)
    def __unicode__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length = 128)
    content = models.TextField(null = False)
    parser = models.CharField(max_length = 1, choices = settings.PARSER_ENGINES)
    restrict_negative = models.BooleanField(default = 0)
    owner = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag)
    blog = models.ForeignKey(Blog)
    created = models.DateTimeField(auto_now = True, auto_now_add = True)
    rating = models.IntegerField(editable = False, default = 0)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return self.title

class PostVote(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    positive = models.BooleanField()
