# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms import ModelForm, CharField, ModelChoiceField
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.contrib.auth.models import User
from userauth.models import Profile
from taverna.blog.models import Blog, Post, Tag
from util import rr
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from forum.views import PostForm as CommentForm

@login_required()
def post_comment(request, post_id):
    form = CommentForm(request.POST)
    if form.is_valid() and request.user.profile.can_create_comment():
        comment = form.save(commit = False)
        comment.blog_post = Post.objects.get(pk = post_id)
        comment.owner = request.user
        comment.save()

        paginator = Paginator(Post.objects.get(pk = post_id).post_set.all(), 5)
        last_page = paginator.num_pages

        return HttpResponseRedirect("%s#post_%s" % ( reverse(post_view, args = [last_page, post_id]), comment.pk) )

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
@rr('blog/add_post.html')
def post_add(request):
    user_blogs = Blog.objects.filter(owner__in = [1, request.user.pk]).order_by('name').order_by('-owner__id')

    class PostForm(ModelForm):
        tag_string = CharField()
        blog = ModelChoiceField(queryset = user_blogs,
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

@rr('blog/post_view.html')
def post_view(request, post_id, page = 1):
    post = Post.objects.get(pk = post_id)
    paginator = Paginator(post.post_set.all(), 5)

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return { 'post': post, 'thread': thread, 'comment_form': CommentForm() }

@rr('blog/blog.html')
def tags_search(request, tag_id, page = 1):
    #FIXME: use paginator for posts view!!!
    blog_posts = None
    try:
        posts = Post.objects.filter(tags = tag_id).order_by('-created')
        paginator = Paginator(posts, 10)

        tag = Tag.objects.get(pk=tag_id);

        try:
            blog_posts = paginator.page(page)
        except (EmptyPage, InvalidPage):
            blog_posts = paginator.page(paginator.num_pages)
    except (Tag.DoesNotExist, Post.DoesNotExist):
        return HttpResponseRedirect("/")

    return {'blog_posts': blog_posts, 'tag': tag }

@rr('blog/blog.html')
def view(request, blog_id, page = 1):
    blog_posts = None
    blog_info = None
    try:
        blog_info = Blog.objects.get(pk = blog_id)
        posts = Post.objects.filter(blog = blog_info).order_by('-created')
        paginator = Paginator(posts, 10)

        try:
            blog_posts = paginator.page(page)
        except (EmptyPage, InvalidPage):
            blog_posts = paginator.page(paginator.num_pages)

    except (Blog.DoesNotExist, Post.DoesNotExist):
        return HttpResponseRedirect("/")

    return {'blog_posts': blog_posts, 'blog_info': blog_info }

@rr('blog/blog.html')
def index(request, page = 1):
    posts = Post.objects.order_by('-created')
    paginator = Paginator(posts, 10)

    try:
        blog_posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        blog_posts = paginator.page(paginator.num_pages)

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

