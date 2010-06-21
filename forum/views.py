from models import *
from util import rr
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum

class PostForm(forms.ModelForm):
    class Meta:
        model = Post

@rr('forum/index.html')
def index(request):
    return {'forums': Forum.objects.all(), 'forum_form': ForumForm()}

@rr('forum/forum.html')
def forum(request, forum_id):
    return {
        'forum': Forum.objects.get(pk = forum_id),
        'form': PostForm(),
    }

def forum_create(request):
    form = ForumForm(request.POST)
    if request.user.profile.is_karma_good() and form.is_valid():
        forum = form.save(commit = False)
        forum.owner = request.user
        forum.save()
        return HttpResponseRedirect(reverse(index))

