# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms import ModelForm, CharField, ModelChoiceField

from django.contrib.auth.models import User
from userauth.models import Profile
from taverna.blog.models import Blog, Tag
from taverna.forum.models import Post, PostEdit

from util import rr, ExtendedPaginator as Paginator
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from forum.views import PostForm as CommentForm

@login_required()
@rr('blog/settings.html')
def settings(request):

    try:
        blog = Blog.objects.get(owner = request.user)
    except Blog.DoesNotExist:
        blog = Blog(name = request.user.username)
        blog.owner = request.user
        blog.save()

    class BlogForm(ModelForm):
        class Meta:
            model = Blog
            exclude = ('owner', 'name')

    form = BlogForm(instance = blog)

    if request.method == 'POST':
        form = BlogForm(request.POST, instance = blog)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(view, args = [blog.pk]))
    return {'form': form}

@login_required()
@rr('blog/post_edit.html')
def post_edit(request, post_id):
    post_orig = Post.objects.get(pk = post_id)

    if not post_orig.reply_to == None:
        return HttpResponseRedirect("/")

    user_blogs = Blog.objects.filter(owner__in = [1, request.user.pk]).order_by('name').order_by('-owner__id')

    tag_string = ""

    class EditForm(ModelForm):
        tag_string = CharField(initial = post_orig.get_tag_list())
        blog = ModelChoiceField(queryset = user_blogs,
                            initial = user_blogs[0],
                            label = _("Post to"))

        class Meta:
            model = Post
            exclude = ('tags', 'reply_to', 'thread')

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
    user_blogs = Blog.objects.filter(owner__in = [1, request.user.pk]).order_by('name').order_by('-owner__id')

    class PostForm(ModelForm):
        tag_string = CharField()
        blog = ModelChoiceField(queryset = user_blogs,
                            initial = user_blogs[0],
                            label = _("Post to"))

        class Meta:
            model = Post
            exclude = ('tags', 'reply_to', 'thread')

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

    page = request.GET.get("offset", 1)

    blog_posts = None

    posts = Post.objects.filter(tags = tag_id).order_by('-created')
    from django.conf import settings
    paginator = Paginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])
    tag = Tag.objects.get(pk=tag_id);

    return {'thread': paginator.page(page), 'tag': tag }

@rr('blog/blog.html')
def view(request, blog_id):
    blog_posts = None
    blog_info = None

    page = request.GET.get("offset", 1)

    blog_info = Blog.objects.get(pk = blog_id)
    posts = Post.objects.filter(blog = blog_info).order_by('-created')
    from django.conf import settings
    paginator = Paginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    return {'thread': paginator.page(page), 'blog_info': blog_info }

@rr('blog/blog.html')
def view_all(request, user_id):
    blog_posts = None
    blog_info = None

    page = request.GET.get("offset", 1)

    posts_owner = User.objects.get(pk = user_id)
    posts = Post.objects.exclude(blog = None,forum = None).filter(owner = user_id).order_by('-created')
    from django.conf import settings
    paginator = Paginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    return {'thread': paginator.page(page), 'posts_owner': posts_owner}

@rr('blog/blog.html')
def index(request):
    posts = Post.objects.exclude(blog = None).order_by('-created')

    page = request.GET.get("offset", 1)

    from django.conf import settings
    paginator = Paginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    return { 'thread': paginator.page(page)}

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
    blog_list = Blog.objects.all().exclude(owner = 1).order_by("-owner__profile__karma")[:10]

    page = request.GET.get("offset", 1)

    from django.conf import settings
    paginator = Paginator(blog_list, settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    return { 'thread': paginator.page(page) }

