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

@login_required(redirect_field_name='/login.html')
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
    try:
        user_info = User.objects.get(username__exact=username)
        user_blog = Blog.objects.get(owner=user_info)
        blog_posts = Post.objects.filter(owner=user_info)
    except (User.DoesNotExist, Blog.DoesNotExist):
        return HttpResponseRedirect('/')

    return {'user_info': user_info,
            'user_blog': user_blog,
            'blog_posts': blog_posts}

@login_required(redirect_field_name='/login.html')
@rr('blog/topic.html')
def addTopic(request):
    try:
        user_blog = Blog.objects.get(owner__exact=request.user)
    except (Blog.DoesNotExist):
        return HttpResponseRedirect('/')

    class TopicEditForm(forms.Form):
        target = forms.ModelChoiceField(queryset=Blog.objects.filter(owner=5),
                                    empty_label=_("My own blog"), required=False)
        title = forms.CharField(required=True, min_length=8, max_length=128)
        content = forms.CharField(required=False,
                              widget=forms.Textarea(attrs={'rows':'25'}))
        parser = forms.CharField(max_length=3,
                    widget=forms.Select(choices=settings.PARSER_ENGINES))

        tags = forms.CharField(required=False, max_length=128)
        allow_negative = forms.BooleanField(required=False, initial=False)

        def save(self):
            target = self.cleaned_data['target']
            content = self.cleaned_data['content']
            title = self.cleaned_data['title']

            try:
                if Post.objects.filter(title__exact=title, blog=target):
                    return
            except Post.DoesNotExist:
                pass

            parser = self.cleaned_data['parser']
            tags = self.cleaned_data['tags']
            allow_negative = self.cleaned_data['allow_negative']

            if not target:
                target = user_blog

            topic = Post(blog=target, title=title, content=content, parser=parser, restrict_negative=allow_negative, owner=request.user)
            topic.save()

            tag_list = tags.split(", ")
            for tag in tag_list:
                t = None
                try:
                    t = Tag.objects.get(name__exact=tag)
                except Tag.DoesNotExist:
                    t = Tag(name=tag)
                    t.save()
                topic.tags.add(t)


    form = None
    preview = None
    tags = None

    if request.method == 'POST':
        form = TopicEditForm(request.POST)
        if form.is_valid():
            if request.POST['submit']==_("Save"):
                form.save()
                return HttpResponseRedirect("/%s/" % request.user.username)
    else:
        form = TopicEditForm()

    return {'form': form}

@rr('blog/traker.html')
def index(request):
    topics = Post.objects.order_by('-created')[:10]
    return { 'topics': topics }
