# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms import ModelForm, CharField, ModelChoiceField

from django.db import IntegrityError

from django.contrib.auth.models import User
from userauth.models import Profile
from taverna.blog.models import Blog, Tag
from taverna.forum.models import Post, PostEdit, PostVote

from util import rr, ExtendedPaginator
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from forum.views import PostForm as CommentForm

from forum.views import modify_rating


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
    if not request.user.profile.can_create_topic:
        return HttpResponseRedirect("/") # FIXME redirect to error message

    post_orig = Post.objects.exclude(removed = True).get(pk = post_id)

    if not request.user.is_superuser:
        if not post_orig.reply_to == None:
            return HttpResponseRedirect("/")

        if post_orig.owner != request.user:
            return HttpResponseRedirect("/")

        user_info = request.user
    else:
        user_info = post_orig.owner

    user_blogs = Blog.objects.filter(owner__in = [1, user_info.pk]).order_by('name').order_by('-owner__id')

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
    if not request.user.profile.can_create_topic():
        return error(request, _("You have not enough karma to create new topic!"))


    user_blogs = Blog.objects.filter(owner__in = [1, request.user.pk]).order_by('name').order_by('-owner__id')

    class PostForm(ModelForm):
        tag_string = CharField()
        blog = ModelChoiceField(queryset = user_blogs,
                            initial = user_blogs[0],
                            label = _("Post to"))

        class Meta:
            model = Post
            exclude = ('tags', 'reply_to', 'thread', 'removed')

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

    posts = Post.objects.exclude(removed = True).filter(tags = tag_id).order_by('-created')
    from django.conf import settings
    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])
    tag = Tag.objects.get(pk=tag_id);

    return {'thread': paginator.page(page), 'tag': tag }

@rr('blog/blog.html')
def view(request, blog_id):
    blog_posts = None
    blog_info = None

    page = request.GET.get("offset", 1)

    blog_info = Blog.objects.get(pk = blog_id)
    posts = Post.objects.exclude(removed = True).filter(blog = blog_info).order_by('-created')
    from django.conf import settings
    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    return {'thread': paginator.page(page), 'blog_info': blog_info }

@rr('blog/blog.html')
def view_all(request, user_id):
    blog_posts = None
    blog_info = None

    page = request.GET.get("offset", 1)

    posts_owner = User.objects.get(pk = user_id)
    posts = Post.objects.exclude(blog = None,forum = None).filter(removed = False, owner = user_id).order_by('-created')
    from django.conf import settings
    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    return {'thread': paginator.page(page), 'posts_owner': posts_owner}

@rr('blog/blog.html')
def index(request):
    posts = Post.objects.exclude(blog = None).filter(removed = False).order_by('-created')

    page = request.GET.get("offset", 1)

    from django.conf import settings
    paginator = ExtendedPaginator(posts, settings.PAGE_LIMITATIONS["BLOG_POSTS"])

    return { 'thread': paginator.page(page)}

@rr('ajax/vote.json', "application/json")
def vote_async(request, post_id, positive):
    post = Post.objects.exclude(removed = True).get(pk = post_id)

    if not request.user.is_authenticated():
        return {"rating": post.rating, "message": _("Registration required.")}

    if post.owner == request.user:
        return {"rating": post.rating, "message": _("You can not vote for own post.")}

    if int(positive) == 0:
        positive = True
    else:
        positive = False

    if not request.user.is_superuser:

        if request.user.profile.use_force(1):
            try:
                PostVote(post = post, user = request.user, positive = positive).save()
            except IntegrityError:
                return {"rating": post.rating, "message": _("You can not vote more then one time for a single post.")}
            else:
                request.user.profile.save()
        else:
            return {"rating": post.rating, "message": _("You not enough force.")}

    modify_rating(post, 1, positive)
    return {"rating": post.rating}

@rr('ajax/vote.json', "application/json")
def vote_generic(request, post_id, positive):
    post = Post.objects.exclude(removed = True).get(pk = post_id)

    if request.user.is_authenticated() and post.owner != request.user:
        if int(positive) == 0:
            positive = True
        else:
            positive = False

        try:
            PostVote(post = post, user = request.user, positive = positive).save()
        except IntegrityError:
            pass
        else:
            modify_rating(post, 1, positive)

    if post.reply_to:
        from django.conf import settings
        paginator = Paginator(Post.objects.filter(thread = post.thread).exclude(pk = post.thread.pk), settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])
        print paginator.page_range
        for page in paginator.page_range:
            if post in paginator.page(page).object_list:
               return HttpResponseRedirect("%s?offset=%i#post_%i" % (reverse("forum.views.thread", args = [post.thread.pk]), page, post.pk))
    else:
        return HttpResponseRedirect(reverse("forum.views.thread", args = [post.pk]))

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
    blog_list = Blog.objects.all().exclude(owner = 1).order_by("-owner__profile__karma")

    page = request.GET.get("offset", 1)

    from django.conf import settings
    paginator = ExtendedPaginator(blog_list, settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    return { 'thread': paginator.page(page) }

@rr('blog/error.html')
def error(request, message):
    return { 'message': message }
