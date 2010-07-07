from models import *
from util import rr
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum

class PostForm(forms.ModelForm):
    class Meta:
        model = Post

@rr('forum/index.html')
def index(request):
    return {'forums': Forum.objects.all()}

@rr('forum/forum.html')
def forum(request, forum_id):
    forum = Forum.objects.get(pk = forum_id)
    return {
        'forum': forum, 
        'post_list': Post.objects.filter(forum = forum, reply_to = None),
        'form': PostForm(),
    }

@rr('forum/thread.html')
def thread(request, post_id):
    post = Post.objects.get(pk = post_id)
    thread = Post.objects.filter(thread = post)[1:]
    return {'post': post, 'thread': thread}

@login_required()
@rr('forum/reply.html')
def reply(request, post_id = None):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit = False)
            if post_id:
                post.reply_to = Post.objects.get(pk = post_id)
                post.thread = post.reply_to.thread
                post.forum = post.reply_to.forum
            else:
                post.forum = Forum.objects.get(pk = request.POST['forum_id'])
            post.owner = request.user
            post.save()
            if not post_id:
                post.thread = post
                post.save()
            redirect = reverse("forum.views.forum", args = [post.forum.pk])
            return HttpResponseRedirect(redirect)
    else:
        form = PostForm()

    if post_id:
        post = Post.objects.get(id = post_id)
    else:
        post = None
    return { 'form': form, 'post': post}

@login_required()
@rr('forum/forum_create.html')
def forum_create(request):
    if request.method == 'GET':
        return {'form': ForumForm()}
    form = ForumForm(request.POST)
    if request.user.profile.can_create_forum() and form.is_valid():
        forum = form.save(commit = False)
        forum.owner = request.user
        forum.save()
        return HttpResponseRedirect(reverse(index))


