# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import forms

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from userauth.models import Profile
from taverna.blogs.models import Blog, Post, Tag
from util import rr
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.conf import settings

@login_required()
@rr('blog/settings.html')
def settings(request):

    try:
        blog = Blog.objects.get(owner = request.user)
    except Blog.DoesNotExist:
        blog = Blog(name = request.user.username)
        blog.owner = request.user
        blog.save()

    class BlogForm(forms.ModelForm):
        class Meta:
            model = Blog
            exclude = ('owner', 'name')

    form = BlogForm(instance = blog)

    if request.method == 'POST':
        form = BlogForm(request.POST, instance = blog)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("blogs.views.view", args = [blog.id]))
    return {'form': form}

@login_required()
@rr('blog/add_post.html')
def post_add(request):
    user_blogs = Blog.objects.filter(owner__in = [1, request.user.id]).order_by('name').order_by('-owner__id')

    class PostForm(forms.ModelForm):
        tag_string = forms.CharField()
        blog = forms.ModelChoiceField(queryset = user_blogs,
            initial = user_blogs[0],
            label = _("Post to"))
        class Meta:
            model = Post
            exclude = ('tags', )
        def save(self, **args):
            post = super(PostForm, self).save(commit = False, **args)
            post.owner = request.user
            post.save()
            for name in [t.strip() for t in self.cleaned_data["tag_string"].split(",")]:
                try:
                    post.tags.add(Tag.objects.get(name = name))
                except Tag.DoesNotExist:
                    tag = Tag(name = name)
                    tag.save()
                    post.tags.add(tag)
            return post.id

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
                    return HttpResponseRedirect(reverse(post_view, args = [post_id]))
    return {
        'form': form,
        'preview': preview,
        'tags': tags,
        'dont_strip': True}

@rr('blog/blog.html')
def post_view(request, post_id):
    blog_posts = None
    blog_info = None
    try:
        blog_posts = Post.objects.filter(pk = post_id)
        blog_info = blog_posts[0].blog
    except (Blog.DoesNotExist, Post.DoesNotExist):
        return HttpResponseRedirect("/")
    return { 'blog_info': blog_info, 'blog_posts': Post.objects.filter(pk = post_id), 'dont_strip': True }

@rr('blog/blog.html')
def view(request, blog_id):
    #FIXME: use paginator for posts view!!!
    blog_posts = None
    blog_info = None
    try:
        blog_info = Blog.objects.get(pk = blog_id)
        blog_posts = Post.objects.filter(blog = blog_info).order_by('-created')[:10]
    except (Blog.DoesNotExist, Post.DoesNotExist):
        return HttpResponseRedirect("/")

    return {'blog_posts': blog_posts, 'blog_info': blog_info }

@rr('blog/blog.html')
def index(request):
    #FIXME: Use paginator for posts view!!!
    blog_posts = Post.objects.order_by('-created')[:10]
    return { 'blog_posts': blog_posts }

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
    #FIXME: Use paginator for posts view!!!
    user_blogs = Blog.objects.all().exclude(owner = 1).order_by("-owner__profile__karma")[:10]
    return { 'user_blogs': user_blogs }

