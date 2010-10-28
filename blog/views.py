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
# along with Taverna. If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms import ModelForm, CharField, ModelChoiceField, Textarea

from django.db import IntegrityError

from django.contrib.auth.models import User
from userauth.models import Profile
from taverna.blog.models import Blog, Tag
from taverna.forum.models import Post, PostEdit, PostVote

from util import rr, ExtendedPaginator
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.http import Http404
from django.core.paginator import InvalidPage, EmptyPage
from django.conf import settings

@login_required()
@rr('blog/settings.html')
def blog_settings(request):
    if request.user.profile.buryed:
       return error(request, "")

    blog = Blog.objects.get(owner = request.user)

    class BlogForm(ModelForm):
        class Meta:
            model = Blog
            exclude = ('owner')

        def save(self, **args):
            blog_name = Blog.objects.get(owner = request.user).name
            blog = super(BlogForm, self).save(commit = False, **args)
            if blog.name == blog_name:
                if request.user.profile.use_force("BLOG_DESC_EDIT"):
                    request.user.profile.save()
                    blog.save()
                else:
                    return error(request, "BLOG_DESC_EDIT")
            else:
                if request.user.profile.use_force("BLOG_NAME_EDIT"):
                    request.user.profile.save()
                    blog.save()
                else:
                    return error(request, "BLOG_NAME_EDIT")
            return HttpResponseRedirect(reverse(view, args = [blog.pk]))

    form = BlogForm(instance = blog)

    if request.method == 'POST':
        form = BlogForm(request.POST, instance = blog)
        if form.is_valid():
            return form.save()

    return {'form': form}

@login_required()
@rr('blog/post_edit.html')
def post_edit(request, post_id):
    if not request.user.profile.can_edit_topic():
        return error(request, "TOPIC_EDIT")

    post_orig = Post.objects.exclude(removed = True).get(pk = post_id)

    if not request.user.is_staff:
        if not post_orig.reply_to == None:
            raise Http404

        if post_orig.owner != request.user:
            raise Http404

        user_info = request.user
    else:
        user_info = post_orig.owner

    user_blogs = Blog.objects.filter(owner__in = [1, user_info.pk]).order_by('name').order_by('-owner__id')

    tag_string = ""

    class EditForm(ModelForm):
        tag_string = CharField(initial = post_orig.get_tag_list())
        blog = ModelChoiceField(queryset = user_blogs,
                            initial = user_blogs[0],
                            label = _("Post to"))

        class Meta:
            model = Post
            exclude = ('tags', 'reply_to', 'thread', 'flags', 'removed', 'closed', 'solved', 'stiked')
            widgets = {
                      'text': Textarea(attrs={'cols': 80, 'rows': 27}),
                      }

        def save(self, **args):
            orig_text = Post.objects.get(pk = post_id).text

            post = super(EditForm, self).save(commit = False, **args)
            post.tags = ""
            post.save()

            PostEdit(post = post, user = request.user, old_text = orig_text, new_text = post.text).save()

            for name in [t.strip() for t in self.cleaned_data["tag_string"].split(",")]:
                try:
                    post.tags.add(Tag.objects.get(name = name))
                except Tag.DoesNotExist:
                    tag = Tag(name = name)
                    tag.save()
                    post.tags.add(tag)

            request.user.profile.use_force("TOPIC_EDIT")
            request.user.profile.save()

    preview = None
    tags = None

    if request.method == 'POST':
        form = EditForm(request.POST, instance=post_orig)
        form.is_valid()
        if 'submit' in request.POST:
            if request.POST['submit']==_("Save"):
                form.save()
                return HttpResponseRedirect(reverse("forum.views.thread", args = [post_id]))
    else:
        form = EditForm(instance=post_orig)
    return {
        'form': form,
        'post_id': post_id,
        'dont_strip': True
        }

@login_required()
@rr('blog/post_add.html')
def post_add(request):
    if not request.user.profile.can_create_topic():
       return error(request, "TOPIC_CREATE")

    user_blogs = Blog.objects.filter(owner__in = [1, request.user.pk]).order_by('name').order_by('-owner__id')

    class PostForm(ModelForm):
        tag_string = CharField(max_length = 32)
        blog = ModelChoiceField(queryset = user_blogs,
                            initial = user_blogs[0],
                            label = _("Post to"))

        class Meta:
            model = Post
            exclude = ('tags', 'reply_to', 'thread', 'flags', 'removed', 'closed', 'solved', 'stiked')
            widgets = {
                      'text': Textarea(attrs={'rows': 27}),
                      }

        def save(self, **args):
            post = super(PostForm, self).save(commit = False, **args)
            post.owner = request.user
            post.save()
            post.thread = post
            post.save()
            for name in [t.strip() for t in self.cleaned_data["tag_string"].split(",")]:
                try:
                    post.tags.add(Tag.objects.get(name = name))
                except Tag.DoesNotExist:
                    tag = Tag(name = name)
                    tag.save()
                    post.tags.add(tag)

            request.user.profile.use_force("TOPIC_CREATE")
            request.user.profile.save()
            return post.blog.pk

    form = PostForm()
    preview = None
    tags = None

    if request.method == 'POST':
        form = PostForm(request.POST)
        form.is_valid()
        if 'submit' in request.POST:
            if form.is_valid():
                if request.POST['submit']==_("Save"):
                    post_id = form.save()
                    return HttpResponseRedirect(reverse(view, args = [post_id]))
    return {
        'form': form,
        'preview': preview,
        'tags': tags,
        'dont_strip': True}

@rr('blog/blog.html')
def tags_search(request, tag_id):

    showall = request.GET.get("showall", 0)
    page = request.GET.get("offset", 1)

    blog_posts = None

    if showall == "1":
        posts = Post.objects.filter(tags = tag_id).order_by('-created')
    else:
        posts = Post.objects.filter(tags = tag_id, removed = False).order_by('-created')

    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])
    tag = Tag.objects.get(pk=tag_id);

    return {'thread': paginator.page(page), 'tag': tag, 'showall': showall}

@rr('blog/blog.html')
def view(request, blog_id):
    blog_posts = None
    blog_info = None

    showall = request.GET.get("showall", 0)
    page = request.GET.get("offset", 1)

    blog_info = Blog.objects.get(pk = blog_id)
    if showall == "1":
        posts = Post.objects.filter(blog = blog_info).order_by('-created')
    else:
        posts = Post.objects.filter(blog = blog_info).exclude(removed = True).order_by('-created')

    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    return {'thread': paginator.page(page), 'blog_info': blog_info, 'showall': showall }

@rr('blog/blog.html')
def view_all(request, user_id):
    blog_posts = None
    blog_info = None

    showall = request.GET.get("showall", 0)
    page = request.GET.get("offset", 1)

    posts_owner = User.objects.get(pk = user_id)
    if showall == "1":
        posts = Post.objects.exclude(blog = None).filter(owner = user_id, forum = None).order_by('-created')
    else:
        from django.db.models import Q
        posts = Post.objects.exclude(blog = None).filter(owner = user_id, forum = None, removed = False).order_by('-created')

    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    return {'thread': paginator.page(page), 'posts_owner': posts_owner, 'showall': showall}

@rr('blog/blog.html')
def index(request):
    showall = request.GET.get("showall", 0)

    if showall == "1":
        posts = Post.objects.exclude(blog = None).order_by('-created')
    else:
        posts = Post.objects.exclude(blog = None).exclude(removed = True).order_by('-created')

    page = request.GET.get("offset", 1)

    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return { 'thread': thread, 'showall': showall }

@rr('ajax/vote.json', "application/json")
def vote_async(request, post_id, positive):
    if not request.user.is_authenticated():
        return {"rating": post.rating, "message": _("Registration required.")}

    post = Post.objects.exclude(removed = True).get(pk = post_id)
    if post.owner == request.user:
        return {"rating": post.rating, "message": _("You can not vote for own post.")}

    if int(positive) == 0:
        positive = True
    else:
        positive = False

    if request.user.profile.use_force("VOTE"):
        try:
            PostVote(post = post, user = request.user, positive = positive).save()
        except IntegrityError:
            return {"rating": post.rating, "message": _("You can not vote more then one time for a single post.")}
        else:
            request.user.profile.save()
    else:
        return {"rating": post.rating, "message": _("You have not enough Force.")}

    from forum.views import modify_rating
    modify_rating(post, 1, positive)
    return {"rating": post.rating}

def vote_generic(request, post_id, positive):
    if not request.user.is_authenticated():
        return error(request, _("Registration required."))

    post = Post.objects.exclude(removed = True).get(pk = post_id)
    if post.owner == request.user:
        return error(request, _("You can not vote for own post."))

    if int(positive) == 0:
        positive = True
    else:
        positive = False

    if request.user.profile.use_force("VOTE"):
        try:
            PostVote(post = post, user = request.user, positive = positive).save()
        except IntegrityError:
            return error(request, _("You can not vote more then one time for a single post."))
        else:
            request.user.profile.save()
    else:
        return error(request, "VOTE")

    from forum.views import modify_rating
    modify_rating(post, 1, positive)

    if post.reply_to:
        paginator = Paginator(Post.objects.filter(thread = post.thread).exclude(pk = post.thread.pk), settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])
        for page in paginator.page_range:
            if post in paginator.page(page).object_list:
               return HttpResponseRedirect("%s?offset=%i#post_%i" % (reverse("forum.views.thread", args = [post.thread.pk]), page, post.pk))
    else:
        return HttpResponseRedirect(reverse("forum.views.thread", args = [post.pk]))

@rr('blog/blog_list.html')
def list(request):
    public_blogs = Blog.objects.filter(owner = 1)
    user_blogs = Blog.objects.all().exclude(owner = 1).order_by("-owner__profile__karma")[:10]
    return { 'public_blogs': public_blogs, 'user_blogs': user_blogs }

@rr('blog/blog_list.html')
def list_public(request):
    public_blogs = Blog.objects.filter(owner = 1)
    return { 'public_blogs': public_blogs }

@rr('blog/blog_list.html')
def list_users(request):
    blog_list = Blog.objects.all().exclude(owner = 1).order_by("-owner__profile__karma")

    page = request.GET.get("offset", 1)

    paginator = ExtendedPaginator(blog_list, settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    return { 'thread': paginator.page(page) }

@rr('blog/error.html')
def error(request, error):
    if request.user.profile.buryed:
        desc = _("Sorry, but You have been buryed at our Grave Yard. See your profile for a details.")
        cost = None
    else:
        try:
            desc = settings.FORCE_PRICELIST[error]["DESC"]
            cost = settings.FORCE_PRICELIST[error]["COST"]
        except KeyError:
            desc = error
            cost = None

    return { 'desc': desc, 'cost': cost }

