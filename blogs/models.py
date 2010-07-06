# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from django.conf import settings

class Blog(models.Model):
    name = models.SlugField(max_length = 32, unique = True)
    desc = models.CharField(max_length = 48, default = _("Blog description"))
    active = models.BooleanField(default = False, editable = False)
    owner = models.ForeignKey(User)
    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length = 32, unique = True)
    def __unicode__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length = 128)
    content = models.TextField(null = False)
    parser = models.IntegerField(choices = settings.PARSER_ENGINES, default = 0)
    restrict_negative = models.BooleanField(_("Restrict user comments with negative carma"), default = 0)
    owner = models.ForeignKey(User, editable = False)
    tags = models.ManyToManyField(Tag)
    blog = models.ForeignKey(Blog)
    created = models.DateTimeField(auto_now = True, auto_now_add = True)
    rating = models.IntegerField(editable = False, default = 0)

    class Meta:
        ordering = ['-created']
        unique_together = ('title', 'blog')

    def __unicode__(self):
        return self.title

class BlogPostVote(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    positive = models.BooleanField()

    class Meta:
        unique_together = ('post', 'user')


