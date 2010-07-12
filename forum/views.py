from models import *
from util import rr
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage

class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('title', )

@rr('forum/index.html')
def index(request):
    return {'forums': Forum.objects.all().order_by('name')}

@rr('forum/forum.html')
def forum(request, forum_id):
    forum = Forum.objects.get(pk = forum_id)
    return {
        'forum': forum,
        'thread_list': Post.objects.filter(forum = forum, reply_to = None).order_by('-created'),
        'form': PostForm(),
    }

@rr('forum/thread.html')
def thread(request, post_id, page = 1):
    startpost = Post.objects.get(pk = post_id)
    paginator = Paginator(Post.objects.filter(thread = startpost)[1:], 5)

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return {'startpost': startpost, 'thread': thread}

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
            post.blog_post = reply_to.blog_post
            post.thread = post.reply_to.thread
            post.forum = post.reply_to.forum
            post.owner = request.user
            post.save()
            if post.forum is None:
                redirect = "%s#post_%s" % (reverse("blog.views.post_view", args = [post.blog_post.pk]), post.pk)
            else:
                redirect = "%s#post_%s" % (reverse("forum.views.thread", args = [post.thread.pk]), post.pk)
            return HttpResponseRedirect(redirect)
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

