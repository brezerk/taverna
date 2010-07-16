from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from blog.models import Blog, Tag
from django.conf import settings
from django.core.urlresolvers import reverse

class Forum(models.Model):
    name = models.CharField(_("Name"), max_length = 64)
    description = models.CharField(_("Description"), max_length = 64)
    owner = models.ForeignKey(User, editable = False)
    rating = models.IntegerField(editable = False, default = 0)
    created = models.DateTimeField(editable = False, auto_now_add = True)

    def get_absolute_url(self):
        return reverse("forum.views.forum", args = [self.pk])


class Post(models.Model):
    owner = models.ForeignKey(User, editable = False, related_name = 'forum_post')
    title = models.CharField(_("Title"), max_length = 64, blank = True, null=False)
    text = models.TextField(_("Text"))
    reply_to = models.ForeignKey('Post', editable = True, blank = True, null = True, related_name = 'reply_')
    thread = models.ForeignKey('Post', editable = True, blank = True, null = True, related_name = 'thread_')
    parser = models.IntegerField(choices = settings.PARSER_ENGINES, default = 0)
    rating = models.IntegerField(editable = False, default = 0)
    created = models.DateTimeField(editable = False, auto_now_add = True)
    restrict_negative = models.BooleanField(_("Restrict user comments with negative carma"), default = 0)
    tags = models.ManyToManyField(Tag, null = True)
    blog = models.ForeignKey(Blog, null = True)
    forum = models.ForeignKey(Forum, editable = False, null = True)
    class Meta:
        ordering = ('created',)

    def get_absolute_url(self):
        return reverse("forum.views.thread", args = [self.pk])

    def get_tag_list(self):
        tag_string = ""

        first = True

        for tag in self.tags.all():
            if first:
                first = False
            else:
                tag_string = tag_string + ", "
            tag_string = tag_string + tag.name

        return tag_string

class PostEdit(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    edited = models.DateTimeField(editable = False, auto_now_add = True)

    class Meta:
        ordering = ["-edited"]

class ForumVote(models.Model):
    forum = models.ForeignKey(Forum)
    user = models.ForeignKey(User)
    positive = models.BooleanField()
    class Meta:
        unique_together = ('forum', 'user')

class PostVote(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    positive = models.BooleanField()
    class Meta:
        unique_together = ('post', 'user')

