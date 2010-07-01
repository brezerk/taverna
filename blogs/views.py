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

@rr('blog/settings.html')
def editBlog(request):

    class BlogForm(forms.ModelForm):
        class Meta:
            model = Blog
    try:
        blog = Blog.objects.get(owner = request.user)
    except Blog.DoesNotExist:
        blog = Blog(name = "%s's blog" % request.user.username)
        blog.owner = request.user
        blog.save()

    form = BlogForm(instance = blog)

    if request.method == 'POST':
        form = BlogForm(request.POST, instance = blog)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/%s/" % request.user.username)
    return {'form': form}

@rr('blog/blog.html')
def viewBlog(request, username):
    #FIXME: use paginator for posts view!!!
    user_info = None
    blog_posts = None
    try:
        user_info = User.objects.get(username = username)
        blog_posts = Post.objects.filter(owner = user_info).order_by('-created')[:10]
    except (User.DoesNotExist, Blog.DoesNotExist):
        return HttpResponseRedirect("/")

    return {'user_info': user_info,
            'blog_posts': blog_posts }

@rr('blog/add_post.html')
def addTopic(request):
    user_blogs = Blog.objects.filter(owner = request.user)

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

    form = PostForm()
    preview = None
    tags = None

    if request.method == 'POST':
        form = PostForm(request.POST)
        form.is_valid()
        if 'submit' in request.POST:
            if form.is_valid():
                if request.POST['submit']==_("Save"):
                    form.save()
                    return HttpResponseRedirect(reverse(viewBlog, args = [request.user.username]))
    return {
        'form': form,
        'preview': preview,
        'tags': tags}

@rr('blog/view_post.html')
def viewPost(request, post):
    return { 'post': Post.objects.get(id = post) }

@rr('blog/traker.html')
def index(request):
    #FIXME: Use paginator for posts view!!!
    topics = Post.objects.order_by('-created')[:10]
    return { 'topics': topics }

@rr('blog/blog_list.html')
def viewBlogsList(request):
    #FIXME: Use paginator for posts view!!!
    public_blogs = Blog.objects.filter(owner = 1)

    user_blogs = Blog.objects.all().exclude(owner = 1).order_by("-owner__profile__karma")[:10]
    return { 'public_blogs': public_blogs, 'user_blogs': user_blogs }
