from models import *
from util import rr, get_offset
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.utils.html import strip_tags

from django.utils.translation import ugettext as _

import re

class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('restrict_negative', 'tags', 'blog', 'reply_to', 'thread')

    def clean_title(self):
        title = self.cleaned_data['title']
        title = title.strip()

        if not title:
            raise forms.ValidationError(_("You have forgotten about title."))

        tag_list = re.split('\[(.*?)\]', title)
        if not tag_list[-1].strip():
            raise forms.ValidationError(_("Tags is good. But title also required."))

        if len(tag_list[-1]) < 5:
            raise forms.ValidationError(_("Topic length < 5 is not allowed."))
        return title

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) < 24:
            raise forms.ValidationError(_("Text length < 24 is not allowed."))
        return text

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('restrict_negative', 'tags', 'blog', 'reply_to', 'thread')

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) < 24:
            raise forms.ValidationError(_("Text length < 24 is not allowed."))
        return text

@rr('forum/index.html')
def index(request):
    return {'forums': Forum.objects.all().order_by('name')}

@rr('forum/forum.html')
def forum(request, forum_id):

    page = get_offset(request)

    forum = Forum.objects.get(pk = forum_id)
    from django.conf import settings
    paginator = Paginator(Post.objects.filter(reply_to = None,forum = forum).order_by('-created'),
                                              settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)

    return {
        'forum': forum,
        'thread': posts,
        'form': PostForm(),
    }

@login_required()
@rr('forum/reply.html')
def reply(request, post_id):
    reply_to = Post.objects.get(pk = post_id)
    if not request.user.profile.can_create_comment():
        return
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit = False)
            post.reply_to = reply_to
#            post.blog = reply_to.blog
            post.thread = post.reply_to.thread
#            post.forum = post.reply_to.forum
            post.owner = request.user
            post.save()

            from django.conf import settings
            paginator = Paginator(Post.objects.filter(thread = post.thread)[1:], settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])
            last_page = paginator.num_pages

            return HttpResponseRedirect("%s?offset=%s#post_%s" % (reverse("forum.views.thread", args = [post.thread.pk]), last_page, post.pk))
    else:
        form = PostForm()
    return { 'form': form, 'post': reply_to}

@login_required()
@rr('forum/topic_create.html')
def topic_create(request, forum_id):
    if not request.user.profile.can_create_topic:
        return
    forum = Forum.objects.get(pk = forum_id)
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            post = form.save(commit = False)
            post.forum = forum
            post.owner = request.user
            post.save()
            post.thread = post
            post.title = strip_tags(post.title)
            post.save()
            return HttpResponseRedirect(reverse('forum.views.forum', args = [forum.pk]))
    else:
        form = ThreadForm()
    return {'form': form}


@login_required()
@rr('forum/forum_create.html')
def forum_create(request):
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if request.user.profile.can_create_forum() and form.is_valid():
            forum = form.save(commit = False)
            forum.owner = request.user
            forum.save()
            return HttpResponseRedirect(reverse(index))
    return {'form': ForumForm()}

@rr('forum/tag_search.html')
def tags_search(request, tag_name):

    page = get_offset(request)

    from django.conf import settings
    paginator = Paginator(Post.objects.filter(title__contains = u"[%s]" % (tag_name),
                                              reply_to = None).order_by('-created'),
                                              settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)

    return {
        'thread': posts,
        'search_tag': tag_name,
    }

@rr('blog/post_view.html')
def thread(request, post_id):

    page = get_offset(request)

    startpost = Post.objects.get(pk = post_id)
    from django.conf import settings
    paginator = Paginator(Post.objects.filter(thread = startpost.thread).exclude(pk = startpost.pk), settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return { 'startpost': startpost, 'thread': thread, 'comment_form': PostForm() }

def offset(request, root_id, offset_id):
    from django.conf import settings
    paginator = Paginator(Post.objects.filter(thread__pk = root_id).exclude(pk = root_id), settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])

    post = Post.objects.get(pk=offset_id)

    for page in paginator.page_range:
        if post in paginator.page(page).object_list:
            return HttpResponseRedirect("%s#post_%s" % (reverse("forum.views.thread", args = [page, root_id]), offset_id))

    return HttpResponseRedirect("/")


