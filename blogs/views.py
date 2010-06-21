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
from taverna.parsers.models import Installed
from util import rr
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

class TopicEditForm(forms.Form):
    target = forms.ModelChoiceField(queryset=Blog.objects.filter(owner_id=5),
                                    empty_label=u"Свой блог", required=False)
    title = forms.CharField(required=True, min_length=8, max_length=128)
    content = forms.CharField(required=False,
                              widget=forms.Textarea(attrs={'rows':'25'}))
    parser = forms.ModelChoiceField(queryset=Installed.objects.all(),
                                    empty_label=None, required=True)
    tags = forms.CharField(required=False, max_length=128)
    allow_negative = forms.BooleanField(required=False, initial=False, label='Extra cheeze')

    def save(self, user, blog):
        target = self.cleaned_data['target']
        content = self.cleaned_data['content']
        title = self.cleaned_data['title']

        try:
            if Post.objects.filter(title__exact=title, blog_id=target):
                return
        except Post.DoesNotExist:
            pass

        parser = self.cleaned_data['parser']
        tags = self.cleaned_data['tags']
        allow_negative = self.cleaned_data['allow_negative']

        if not target:
            target = blog

        topic = Post(blog_id=target, title=title, content=content, parser_id=parser, restrict_negative=allow_negative, owner_id=user)
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

@rr('blog/settings.html')
def editBlog(request):

    class BlogForm(forms.ModelForm):
        class Meta:
            model = Blog
    try:
        blog = Blog.objects.get(owner_id = request.user)
    except Blog.DoesNotExist:
        blog = Blog(name = "%s's blog" % request.user.username)
        blog.owner_id = request.user
        blog.save()

    form = BlogForm(instance = blog)

    if request.method == 'POST':
        form = BlogForm(request.POST, instance = blog)
        if form.is_valid():
            form.save()
    return {'form': form}

def viewBlog(request, username):
    try:
        user_info = User.objects.get(username__exact=username)
        user_blog = Blog.objects.get(owner_id=user_info)
        blog_posts = Post.objects.filter(owner_id=user_info)
    except (User.DoesNotExist, Blog.DoesNotExist):
        return HttpResponseRedirect('/')

    return render_to_response("blog/blog.html", {'user_info': user_info,
                              'user_blog': user_blog,
                              'blog_posts': blog_posts},
                              context_instance=RequestContext(request))

@csrf_protect
def addTopic(request, username):
    if (request.user.username != username):
        return HttpResponseRedirect('/')

    try:
        user_info = User.objects.get(username__exact=username)
        user_blog = Blog.objects.get(owner_id__exact=user_info)
    except (User.DoesNotExist, Blog.DoesNotExist):
        return HttpResponseRedirect('/')

    form = None
    preview = None
    tags = None

    if request.method == 'POST':
        form = TopicEditForm(request.POST)
        if form.is_valid():
            if request.POST['submit']==_("Save"):
                form.save(user_info, user_blog)
                return HttpResponseRedirect('/' + username + '/')
    else:
        form = TopicEditForm()

    return render_to_response("blog/topic.html", {'user_info': user_info,
                              'user_blog': user_blog,
                              'form': form,
                              'preview': preview,
                              'tags': tags},
                              context_instance=RequestContext(request))

@rr('base.html')
def index(request):
    return {}
