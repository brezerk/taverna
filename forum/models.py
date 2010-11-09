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

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from blog.models import Blog, Tag
from userauth.models import ReasonList
from django.conf import settings
from django.core.urlresolvers import reverse
from parsers.templatetags import markup
from django.db.models.signals import post_save
from cache import CacheManager
from django.core.cache import cache


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
    tags = models.ManyToManyField(Tag, null = True)
    blog = models.ForeignKey(Blog, null = True)
    forum = models.ForeignKey(Forum, editable = False, null = True)
    removed = models.BooleanField(editable = True, default = 0)
    sticked = models.BooleanField(editable = True, default = 0)
    closed = models.BooleanField(editable = True, default = 0)
    solved = models.BooleanField(editable = True, default = 0)

    class Meta:
        ordering = ('created',)

    def is_removed(self):
        return bool(settings.O_REMOVED & self.flags)

    def get_absolute_url(self):
        return reverse("forum.views.thread", args = [self.pk])

    def get_section_name(self):
        if self.blog:
            return self.blog.name
        else:
            return self.forum.name

    def get_rating(self):
        """
            Bacouse we use cache system,
            it is more efficeint to droop one model, them 100500 of relatid
            while rating updates, so here is a hack for it
        """
        manager = CacheManager()
        post = manager.request_cache("posts.%s" % (self.pk), Post.objects.get(pk = self.pk))
        return post.rating

    def get_section_type(self):
        if self.blog:
            return _("Blog")
        else:
            return _("Forum")

    def get_section_url(self):
        if self.blog:
            return reverse("blog.views.view", args = [self.blog.pk])
        else:
            return reverse("forum.views.forum", args = [self.forum.pk])

    def get_title(self):
        if self.title:
            return self.title
        else:
            return self.thread.title

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
        manager = CacheManager()
        count_url = manager.request_cache("posts.%s.comments.url" % (self.pk))

        if count_url is None:
            from django.core.paginator import Paginator
            paginator = Paginator(
                        manager.request_cache("posts.%s.comments.all" % (self.pk),
                        Post.objects.exclude(pk=self.pk).filter(thread=self.pk, removed = False)),
                        settings.PAGE_LIMITATIONS["FORUM_COMMENTS"]
                    )

            thread_url = reverse("forum.views.thread", args = [self.pk])
            count_url = "<a href='%s'>%s: %s</a>" % (thread_url, _("Comments"), paginator.count)

            if paginator.num_pages > 1:
                count_url = count_url + " (%s" % (_("page"))
                for page in paginator.page_range:
                    if page != 1:
                        page_url = " <a href='%s?offset=%s'>%s</a>" % (thread_url, page, page)
                        count_url = count_url + page_url

                count_url = count_url + ")"
            manager.request_cache("posts.%s.comments.url" % (self.pk), count_url)

        return count_url

    def get_flags(self):
        ret = ""
        if self.removed:
            ret = "<span class='removed'>&times;</span>"
        if self.sticked:
            ret = ret + "<span class='sticked'>&curren;</span>"
        if self.closed:
            ret = ret + "<span class='solved'>&#33;</span>"
        if self.solved:
            ret = ret + "<span class='solved'>&#63;</span>"
        return ret

    def get_text(self):
        text = markup.strip_cut(self.text)
        return markup.markup(text, self.parser)

    def get_edit_url(self):
        if self.blog:
           return reverse("blog.views.post_edit", args=[self.pk])
        if self.forum:
           return reverse("forum.views.topic_edit", args=[self.pk])

    def get_strip_text(self):
        return markup.strippost(self.text, self)

    def is_edited(self):
        manager = CacheManager()
        lastedit = manager.request_cache("postedit.%s.all" % (self.pk), self.postedit_set.all())

        if lastedit:
            return True
        else:
            return False

    def get_last_edit_user_url(self):
        manager = CacheManager()
        edits = manager.request_cache("postedit.%s.all" % (self.pk), self.postedit_set.all())

        return reverse("userauth.views.profile_view", args=[edits[0].user.pk])

    def get_last_edit_user(self):
        manager = CacheManager()
        edits = manager.request_cache("postedit.%s.all" % (self.pk), self.postedit_set.all())
        return edits[0].user.profile.visible_name

    def get_last_edit_date(self):
        manager = CacheManager()
        edits = manager.request_cache("postedit.%s.all" % (self.pk), self.postedit_set.all())
        return edits[0].edited

    def get_last_edit_url(self):
        manager = CacheManager()
        edits = manager.request_cache("postedit.%s.all" % (self.pk), self.postedit_set.all())
        return reverse("forum.views.post_diff", args=[edits[0].pk])

    def get_edited_count(self):
        manager = CacheManager()
        edits = manager.request_cache("postedit.%s.all" % (self.pk), self.postedit_set.all())
        return edits.count()

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
        _("Result {time} by {user}".format(time=self.edited, user=self.user.profile.visible_name)), context=False)

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
    auto = models.BooleanField(default = 0, editable = False)
    reason = models.ForeignKey(ReasonList, blank = True, null = True, verbose_name=_("Post remove reason"))
    class Meta:
        unique_together = ('post', 'user')

    def get_reason(self):
        ret = "%s (-%s)" % (self.reason, self.reason.cost)
        if self.auto:
            return _("(Auto) Reply to: ") + ret
        else:
            return ret

def Post_cache_manager(sender, instance, created, **kwargs):
    manager = CacheManager()

    print sender

    if instance.blog is not None:
        manager.clear_template_cache("post_main", instance.pk)
        manager.clear_template_cache("post_free", instance.pk)
        manager.clear_template_cache("startpost_main", instance.pk)
        manager.clear_template_cache("startpost_free", instance.pk)
        manager.clear_cache("posts.blog.all")
        manager.clear_cache("posts.blog.%s" % (instance.blog.pk))
        manager.delete_cache("posts.%s" % (instance.pk))
    elif instance.forum is not None:
        pass
    elif instance.blog is None and instance.forum is None:
        manager.clear_cache("posts.%s.comments" % instance.pk)

def PostEdit_cache_manager(sender, instance, created, **kwargs):
    manager = CacheManager()
    manager.clear_cache("postedit.%s.all" % instance.post.pk)

#post_save.connect(Post_cache_manager, sender=Post, dispatch_uid="Post_cache_manager")
#post_save.connect(PostEdit_cache_manager, sender=PostEdit, dispatch_uid="PostEdit_cache_manager")

