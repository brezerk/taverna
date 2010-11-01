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

from models import *
from util import rr
from django import forms
from django.conf import settings
from django.forms import ModelForm, Textarea
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from util import ExtendedPaginator
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from blog.views import error
from django.http import Http404

from django.utils.datastructures import MultiValueDictKeyError

from django.utils.html import strip_tags

from django.utils.translation import ugettext as _

import re

from django.contrib.sites.models import Site


class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('tags', 'blog', 'reply_to', 'thread', 'flags', 'removed', 'solved', 'sticked', 'closed')
        widgets = {
                  'text': Textarea(attrs={'cols': 80, 'rows': 27}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        title = title.strip()

        if not title:
            raise forms.ValidationError(_("You have forgotten about title."))

        tag_list = re.split('\[(.*?)\]', title)
        if not tag_list[-1].strip():
            raise forms.ValidationError(_("Tags is good. But title also required."))

        if len(tag_list[-1].strip()) < 5:
            raise forms.ValidationError(_("Topic length < 5 is not allowed."))
        return title

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        txt_len = len(text)
        if txt_len < 4:
            raise forms.ValidationError(_("Text length < 4 characters is not allowed."))
        elif txt_len > 512:
            raise forms.ValidationError(_("Text length > 512 characters is not allowed."))
        return text

class AdminThreadForm(ThreadForm):
    class Meta:
        model = Post
        exclude = ('tags', 'blog', 'reply_to', 'thread', 'flags', 'removed', 'solved')
        widgets = {
                  'text': Textarea(attrs={'cols': 80, 'rows': 27}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('tags', 'blog', 'reply_to', 'thread', 'flags', 'removed', 'solved', 'sticked', 'closed')
        widgets = {
                  'text': Textarea(attrs={'cols': 80, 'rows': 27}),
        }

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        txt_len = len(text)
        if txt_len < 4:
            raise forms.ValidationError(_("Text length < 4 characters is not allowed."))
        elif txt_len > 512:
            raise forms.ValidationError(_("Text length > 512 characters is not allowed."))
        return text

@rr('forum/index.html')
def index(request):
    return {'forums': Forum.objects.all().order_by('name')}

@rr('forum/forum.html')
def forum(request, forum_id):

    page = request.GET.get("offset", 1)
    showall = request.GET.get("showall", 1)

    forum = Forum.objects.get(pk = forum_id)
    if showall == "1":
        pages = Post.objects.filter(reply_to = None, forum = forum).order_by('-sticked', '-created')
    else:
        pages = Post.objects.filter(reply_to = None, forum = forum, removed = False).order_by('-sticked', '-created')

    paginator = ExtendedPaginator(pages, settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    posts = paginator.page(page)

    return {
        'forum': forum,
        'thread': posts,
        'form': PostForm(),
        'showall': showall,
    }

@rr('forum/traker.html')
def traker(request):
    user_info = User.objects.get(pk = request.user.pk)

    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    showall = request.GET.get("showall", 1)

    if showall == "1":
        pages = Post.objects.filter(blog = None).exclude(owner = user_info).order_by('-created')
    else:
        pages = Post.objects.filter(blog = None, removed = False).exclude(owner = user_info).order_by('-created')

    paginator = Paginator(pages, settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return {'thread': thread, 'user_info': user_info, 'request_url': request.get_full_path(), 'showall': showall }

@login_required()
@rr('forum/reply.html')
def reply(request, post_id):
    reply_to = Post.objects.filter(removed = False, closed = False).get(pk = post_id)

    if reply_to.thread.closed:
        raise Http404

    if not request.user.profile.can_create_comment():
        return error(request, "COMMENT_CREATE")

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            if request.POST['submit']==_("Reply"):
                post = form.save(commit = False)
                post.reply_to = reply_to
                post.thread = post.reply_to.thread
                post.owner = request.user
                post.save()

                request.user.profile.use_force("COMMENT_CREATE")
                request.user.profile.save()

                paginator = ExtendedPaginator(Post.objects.filter(thread = post.thread)[1:], settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])
                last_page = paginator.num_pages

                return HttpResponseRedirect("%s?offset=%s#post_%s" % (reverse("forum.views.thread", args = [post.thread.pk]), last_page, post.pk))
    else:
        form = PostForm()
    return { 'form': form, 'post': reply_to}

@login_required()
@rr('blog/post_remove.html')
def post_view(request, post_id):
    startpost = Post.objects.get(pk = post_id)
    reason = PostVote.objects.exclude(reason = None).get(post = startpost)

    if startpost.reply_to:
        return { 'post': startpost, 'reason': reason }
    else:
        return { 'startpost': startpost, 'reason': reason }

@login_required()
@rr('blog/post_remove.html')
def remove(request, post_id):
    if not request.user.is_staff:
        raise Http404

    if request.user.profile.buryed:
       return error(request, "")

    startpost = Post.objects.exclude(removed = True).get(pk = post_id)

    class RemoveForm(forms.ModelForm):
        class Meta:
            model = PostVote
            exclude = ('post', 'user', 'positive')

        def clean_reason(self):
            reason = self.cleaned_data['reason']
            if reason == None:
                raise forms.ValidationError(_("Valid reason required."))
            return reason

        def save(self, **args):
            postvote = super(RemoveForm, self).save(commit = False, **args)
            postvote.post = startpost
            postvote.user = request.user
            postvote.positive = False
            postvote.auto = False
            postvote.save()

            startpost.removed = True
            modify_rating(startpost, postvote.reason.cost)
            auto_remove(startpost, postvote.reason);

    if request.method == 'POST':
        form = RemoveForm(request.POST)
        form.fields['reason'].empty_label=None
        if form.is_valid():
            form.save()
            if startpost.reply_to:
                offset = request.GET.get("offset", 1)
                return HttpResponseRedirect("%s?offset=%s" % (reverse('forum.views.thread', args = [startpost.thread.pk]), offset))
            else:
                if startpost.forum:
                    return HttpResponseRedirect(reverse('forum.views.forum', args = [startpost.forum.pk]))
                else:
                    return HttpResponseRedirect(reverse('blog.views.view', args = [startpost.blog.pk]))
    else:
        form = RemoveForm()
        form.fields['reason'].empty_label=None

    if startpost.reply_to:
        return { 'post': startpost, 'form': form }
    else:
        return { 'startpost': startpost, 'form': form }

def auto_remove(startpost, reason):
    if startpost.reply_to == None:
        for post in Post.objects.filter(thread = startpost.pk, removed = False):
            PostVote(user = User.objects.get(pk = 1), post = post, reason = reason, positive = False, auto = True).save()
            post.removed = True

            modify_rating(post, reason.cost)
    else:
        for post in Post.objects.filter(reply_to = startpost.pk, removed = False):
            PostVote(user = User.objects.get(pk = 1), post = post, reason = reason, positive = False, auto = True).save()
            post.removed = True

            modify_rating(post, reason.cost)
            auto_remove(post, reason)

def modify_rating(post, cost = 1, positive = False):
    if positive:
        post.rating += cost
        post.owner.profile.karma += cost
    else:
        post.rating -= cost
        post.owner.profile.karma -= cost
        post.owner.profile.force -= cost

    post.owner.profile.save()
    post.save()

@login_required()
@rr('forum/topic_create.html')
def topic_create(request, forum_id):
    if not request.user.profile.can_create_topic():
        return error(request, "TOPIC_CREATE")

    forum = Forum.objects.get(pk = forum_id)
    if request.method == 'POST':
        if request.user.is_staff:
            form = AdminThreadForm(request.POST)
        else:
            form = ThreadForm(request.POST)
        if form.is_valid():
            if request.POST['submit']==_("Post new topic"):
                post = form.save(commit = False)
                post.forum = forum
                post.owner = request.user
                post.save()
                post.thread = post
                post.title = strip_tags(post.title)
                post.save()

                request.user.profile.use_force("TOPIC_CREATE")
                request.user.profile.save()

                return HttpResponseRedirect(reverse('forum.views.forum', args = [forum.pk]))
    else:
        if request.user.is_staff:
            form = AdminThreadForm()
        else:
            form = ThreadForm()
        form.exclude = ('tags', 'blog', 'reply_to', 'thread', 'flags', 'removed', 'solved', 'sticked')
    return {'form': form, 'forum': forum, 'blog_info': True}

@login_required()
@rr('forum/topic_edit.html')
def topic_edit(request, topic_id):
    if not request.user.profile.can_edit_topic():
        return error(request, "TOPIC_EDIT")

    topic = Post.objects.exclude(removed=True).get(pk = topic_id)

    if not topic.reply_to == None:
        raise Http404

    if not topic.owner == request.user:
        raise Http404

    if request.method == 'POST':
        if request.user.is_staff:
            form = AdminThreadForm(request.POST, instance=topic)
        else:
            form = ThreadForm(request.POST, instance=topic)
        if form.is_valid():
            if request.POST['submit']==_("Save"):
                orig_text = Post.objects.get(pk = topic_id).text
                post = form.save()
                if orig_text != post.text:
                    PostEdit(post = topic, user = request.user, old_text = orig_text, new_text = post.text).save()

                request.user.profile.use_force("TOPIC_EDIT")
                request.user.profile.save()

                return HttpResponseRedirect(reverse('forum.views.thread', args = [topic_id]))

    else:
        if request.user.is_staff:
            form = AdminThreadForm(instance=topic)
        else:
            form = ThreadForm(instance=topic)
    return {'form': form, 'blog_info': True}

@login_required()
@rr('forum/forum_create.html')
def forum_create(request):
    if not request.user.profile.can_create_forum():
        return error(request, "FORUM_CREATE")

    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            forum = form.save(commit = False)
            forum.owner = request.user
            forum.save()

            request.user.profile.use_force("FORUM_CREATE")
            request.user.profile.save()

            return HttpResponseRedirect(reverse(index))

    return {'form': ForumForm()}

@rr('forum/tag_search.html')
def tags_search(request, tag_name):

    page = request.GET.get("offset", 1)
    showall = request.GET.get("showall", 0)

    if showall == "1":
        posts = Post.objects.filter(title__contains = u"[%s]" % (tag_name)).order_by('-created')
    else:
        posts = Post.objects.filter(title__contains = u"[%s]" % (tag_name), removed = False).order_by('-created')

    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    return {
        'thread': paginator.page(page),
        'search_tag': tag_name,
        'showall': showall
    }

@rr('blog/post_diff.html')
def post_diff(request, diff_id):
    edit_post = PostEdit.objects.get(pk = diff_id)
    return {'startpost': edit_post.post, 'edit_post': edit_post}

def post_rollback(request, diff_id):
    if not request.user.profile.can_edit_topic():
        return error(request, "TOPIC_EDIT")

    diff = PostEdit.objects.exclude(removed = True).get(pk = diff_id)

    if not diff.post.owner == request.user:
        raise Http404

    PostEdit(post = diff.post, user = request.user, old_text = diff.post.text, new_text = diff.old_text).save()

    request.user.profile.use_force("FORUM_CREATE")
    request.user.profile.save()

    post = diff.post
    post.text = diff.old_text
    post.save()

    return thread(request, post.pk)

def post_solve(request, post_id):
    post = Post.objects.filter(removed = False).get(pk = post_id)

    if post.solved:
        post.solved = False
    else:
        post.solved = True
    post.save()

    if request.user.is_staff or request.user == post.owner:
        return HttpResponseRedirect(reverse("forum.views.thread", args = [post_id]))
    else:
        raise Http404

@rr('blog/post_view.html')
def thread(request, post_id):
    page = request.GET.get("offset", 1)
    showall = request.GET.get("showall", 0)

    startpost = Post.objects.get(pk = post_id)

    if showall == "1":
        paginator = ExtendedPaginator(Post.objects.filter(thread = startpost.thread).exclude(pk = startpost.pk), settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])
    else:
        paginator = ExtendedPaginator(Post.objects.filter(thread = startpost.thread, removed = False).exclude(pk = startpost.pk), settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return { 'startpost': startpost, 'thread': thread, 'showall': showall, 'blog_info': True, 'showedits': True }

@rr('blog/post_print.html')
def print_post(request, post_id):
    return {'startpost': Post.objects.exclude(removed = True).get(pk = post_id), 'site': Site.objects.get_current().domain}

def offset(request, root_id, offset_id):
    if offset_id == root_id:
        return HttpResponseRedirect(reverse('forum.views.thread', args = [root_id]))
    else:
        showall = request.GET.get("showall", 0)

        if showall == "1":
            pages = Post.objects.filter(thread__pk = root_id).exclude(pk = root_id)
        else:
            pages = Post.objects.filter(thread__pk = root_id).exclude(pk = root_id, removed = True)

        paginator = Paginator(pages, settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])
        post = Post.objects.get(pk=offset_id)

        for page in paginator.page_range:
            if post in paginator.page(page).object_list:
                if showall == "1":
                   return HttpResponseRedirect("%s?showall=1&offset=%s#post_%s" % (reverse("forum.views.thread", args = [root_id]), page, offset_id))
                else:
                    return HttpResponseRedirect("%s?offset=%s#post_%s" % (reverse("forum.views.thread", args = [root_id]), page, offset_id))

    raise Http404
