# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from taverna.parsers.models import Installed

# Create your models here.
class Blog(models.Model):
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=48, null=True, blank=True)
    active = models.BooleanField(default=0)
    owner_id = models.ForeignKey(User)
    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    def __unicode__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField(null=False)
    parser_id = models.ForeignKey(Installed)
    restrict_negative = models.BooleanField(default=0)
    owner_id = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag)
    blog_id = models.ForeignKey(Blog)
    adddate = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        ordering = ['-adddate']

    def __unicode__(self):
        return self.title

