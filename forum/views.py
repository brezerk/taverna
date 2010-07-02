from models import *
from util import rr
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

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
    return {
        'forum': Forum.objects.get(pk = forum_id),
        'form': PostForm(),
    }

@rr('forum/thread.html')
def thread(request, post_id):
    def tree(post):
        yield render_to_string('forum/post.include.html', {'post': post})
        for child in post.post_set.all():
            for r in tree(child):
                yield r
            yield '</ul>'
        yield '</li>'

    post = Post.objects.get(pk = post_id)
    return {'post': post, 'tree': tree(post)}

@rr('forum/reply.html')
def reply(request, forum_id = None, post_id = None):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit = False)
            if forum_id:
                post.forum = Forum.objects.get(pk = forum_id)
                redirect = reverse(forum, args = [forum_id])
            else:
                post.reply_to = Post.objects.get(pk = post_id)
                redirect = reverse(thread, args = [post.reply_to.pk])
            post.owner = request.user
            post.save()
            return HttpResponseRedirect(redirect)
    else:
        form = PostForm()
    return {'form': form}

@rr('forum/forum_create.html')
def forum_create(request):
    if request.method == 'GET':
        return {'form': ForumForm()}
    form = ForumForm(request.POST)
    if request.user.profile.is_karma_good() and form.is_valid():
        forum = form.save(commit = False)
        forum.owner = request.user
        forum.save()
        return HttpResponseRedirect(reverse(index))


