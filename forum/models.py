# -*- coding: utf-8 -*-

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

    def get_section_name(self):
        if self.blog:
            return self.blog.name
        else:
            return self.forum.name

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

    def get_tag_url_list(self):
        tag_string = ""

        first = True

        for tag in self.tags.all():
            if first:
                first = False
            else:
                tag_string = tag_string + ", "
            tag_string = tag_string + "<a href='%s'>%s</a>" % (reverse("blog.views.tags_search", args = [tag.pk]) ,tag.name)

        return tag_string

    def get_comments_count(self):
        return Post.objects.exclude(pk=self.pk).filter(thread=self.pk).count()

class PostEdit(models.Model):
    post = models.ForeignKey(Post)
    new_text = models.TextField()
    old_text = models.TextField()
    user = models.ForeignKey(User)
    edited = models.DateTimeField(editable = False, auto_now_add = True)

    class Meta:
        ordering = ["-edited"]

    def get_diff(self):
        import difflib
        differ = difflib.HtmlDiff(tabsize=4,wrapcolumn=60)
        return differ.make_table(self.old_text.splitlines(1), self.new_text.splitlines(1), 
        _("Source %s" % self.post.created), 
        _("Result %s by %s" % (self.edited, self.user.profile.visible_name)), context=False)

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

