from models import *
from util import rr
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from util import ExtendedPaginator
from django.core.paginator import Paginator
from blog.views import error
from django.http import Http404

from django.utils.html import strip_tags

from django.utils.translation import ugettext as _

import re

from django.contrib.sites.models import Site

class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('restrict_negative', 'tags', 'blog', 'reply_to', 'thread', 'removed')

    def clean_title(self):
        title = self.cleaned_data['title']
        title = title.strip()

        if not title:
            raise forms.ValidationError(_("You have forgotten about title."))

        tag_list = re.split('\[(.*?)\]', title)
        if not tag_list[-1].strip():
            raise forms.ValidationError(_("Tags is good. But title also required."))

        if len(tag_list[-1].strip()) < 5:
            raise forms.ValidationError(_("Topic length < 5 is not allowed."))
        return title

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        if len(text) < 24:
            raise forms.ValidationError(_("Text length < 24 is not allowed."))
        return text

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('restrict_negative', 'tags', 'blog', 'reply_to', 'thread', 'removed')

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        if len(text) < 24:
            raise forms.ValidationError(_("Text length < 24 is not allowed."))
        return text

@rr('forum/index.html')
def index(request):
    return {'forums': Forum.objects.all().order_by('name')}

@rr('forum/forum.html')
def forum(request, forum_id):

    page = request.GET.get("offset", 1)

    forum = Forum.objects.get(pk = forum_id)
    from django.conf import settings
    paginator = ExtendedPaginator(Post.objects.filter(reply_to = None,
    forum = forum, removed = False).order_by('-created'),
    settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    posts = paginator.page(page)

    return {
        'forum': forum,
        'thread': posts,
        'form': PostForm(),
    }

@login_required()
@rr('forum/reply.html')
def reply(request, post_id):
    reply_to = Post.objects.exclude(removed = True).get(pk = post_id)
    if not request.user.profile.can_create_comment():
        from django.conf import settings
        return error(request, "%s<br>%s: %s points" % (_("You have not enough Force to create comments!"),
        _("Amount of Force required for this action"), settings.FORCE_PRICELIST["COMMENT_CREATE"])
        )

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            if request.POST['submit']==_("Reply"):
                post = form.save(commit = False)
                post.reply_to = reply_to
                post.thread = post.reply_to.thread
                post.owner = request.user
                post.save()

                from django.conf import settings
                paginator = ExtendedPaginator(Post.objects.filter(thread = post.thread)[1:], settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])
                last_page = paginator.num_pages

                return HttpResponseRedirect("%s?offset=%s#post_%s" % (reverse("forum.views.thread", args = [post.thread.pk]), last_page, post.pk))
    else:
        form = PostForm()
    return { 'form': form, 'post': reply_to}

@login_required()
@rr('blog/post_remove.html')
def post_view(request, post_id):
    startpost = Post.objects.get(pk = post_id)
    reason = PostVote.objects.exclude(reason = None).get(post = startpost)

    if startpost.reply_to:
        return { 'post': startpost, 'reason': reason }
    else:
        return { 'startpost': startpost, 'reason': reason }

@login_required()
@rr('blog/post_remove.html')
def remove(request, post_id):
    if not request.user.is_superuser:
        raise Http404

    startpost = Post.objects.exclude(removed = True).get(pk = post_id)

    class RemoveForm(forms.ModelForm):
        class Meta:
            model = PostVote
            exclude = ('post', 'user', 'positive')

        def clean_reason(self):
            reason = self.cleaned_data['reason']
            if reason == None:
                raise forms.ValidationError(_("Valid reason required."))
            return reason

        def save(self, **args):
            postvote = super(RemoveForm, self).save(commit = False, **args)
            postvote.post = startpost
            postvote.user = request.user
            postvote.positive = False
            postvote.auto = False
            postvote.save()

            startpost.removed = True
            modify_rating(startpost, postvote.reason.cost)
            auto_remove(startpost, postvote.reason);

    if request.method == 'POST':
        form = RemoveForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = RemoveForm()

    if startpost.reply_to:
        return { 'post': startpost, 'form': form }
    else:
        return { 'startpost': startpost, 'form': form }

def auto_remove(startpost, reason):
    if startpost.reply_to == None:
        for post in Post.objects.filter(thread = startpost.pk, removed = False):
            PostVote(user = User.objects.get(pk = 1), post = post, reason = reason, positive = False, auto = True).save()
            post.removed = True

            modify_rating(post, reason.cost)
    else:
        for post in Post.objects.filter(reply_to = startpost.pk, removed = False):
            PostVote(user = User.objects.get(pk = 1), post = post, reason = reason, positive = False, auto = True).save()
            post.removed = True

            modify_rating(post, reason.cost)
            auto_remove(post, reason)

def modify_rating(post, cost = 1, positive = False):
    if positive:
        post.rating += cost
        post.owner.profile.karma += cost
    else:
        post.rating -= cost
        post.owner.profile.karma -= cost
        post.owner.profile.force -= cost

    post.owner.profile.save()
    post.save()

@login_required()
@rr('forum/topic_create.html')
def topic_create(request, forum_id):
    if not request.user.profile.can_create_topic():
        from django.conf import settings
        return error(request, "%s<br>%s: %s points" % (_("You have not enough Force to create topics!"),
        _("Amount of Force required for this action"), settings.FORCE_PRICELIST["TOPIC_CREATE"])
        )

    forum = Forum.objects.get(pk = forum_id)
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            if request.POST['submit']==_("Post new topic"):
                post = form.save(commit = False)
                post.forum = forum
                post.owner = request.user
                post.save()
                post.thread = post
                post.title = strip_tags(post.title)
                post.save()
                return HttpResponseRedirect(reverse('forum.views.forum', args = [forum.pk]))
    else:
        form = ThreadForm()
    return {'form': form, 'forum': forum}

@login_required()
@rr('forum/topic_edit.html')
def topic_edit(request, topic_id):
    if not request.user.profile.can_create_topic:
        return HttpResponseRedirect("/") # FIXME redirect to error message

    topic = Post.objects.exclude(removed = True).get(pk = topic_id)

    if not topic.reply_to == None:
        raise Http404

    if not topic.owner == request.user:
        raise Http404

    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=topic)
        if form.is_valid():
            if request.POST['submit']==_("Save"):
                orig_text = Post.objects.get(pk = topic_id).text
                post = form.save()
                PostEdit(post = topic, user = request.user, old_text = orig_text, new_text = post.text).save()

                return HttpResponseRedirect(reverse('forum.views.thread', args = [topic_id]))

    else:
        form = ThreadForm(instance=topic)
    return {'form': form, 'forum': topic.forum}

@login_required()
@rr('forum/forum_create.html')
def forum_create(request):
    if not request.user.profile.can_create_forum():
        from django.conf import settings
        return error(request, "%s<br>%s: %s points" % (_("You have not enough Force to create forums!"),
        _("Amount of Force required for this action"), settings.FORCE_PRICELIST["FORUM_CREATE"])
        )

        form = ForumForm(request.POST)
        if request.user.profile.can_create_forum() and form.is_valid():
            forum = form.save(commit = False)
            forum.owner = request.user
            forum.save()
            return HttpResponseRedirect(reverse(index))
    return {'form': ForumForm()}

@rr('forum/tag_search.html')
def tags_search(request, tag_name):

    page = request.GET.get("offset", 1)

    from django.conf import settings
    paginator = ExtendedPaginator(Post.objects.filter(title__contains = u"[%s]" % (tag_name),
                                              reply_to = None, removed = False).order_by('-created'),
                                              settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    return {
        'thread': paginator.page(page),
        'search_tag': tag_name,
    }

@rr('blog/post_diff.html')
def post_diff(request, diff_id):
    edit_post = PostEdit.objects.get(pk = diff_id)
    return {'startpost': edit_post.post, 'edit_post': edit_post}

def post_rollback(request, diff_id):

    if not request.user.profile.can_create_topic:
        return HttpResponseRedirect("/") # FIXME redirect to error message

    diff = PostEdit.objects.exclude(removed = False).get(pk = diff_id)

    if not diff.post.owner == request.user:
        raise Http404

    PostEdit(post = diff.post, user = request.user, old_text = diff.post.text, new_text = diff.old_text).save()

    post = diff.post
    post.text = diff.old_text
    post.save()

    return thread(request, post.pk)



@rr('blog/post_view.html')
def thread(request, post_id):

    page = request.GET.get("offset", 1)

    startpost = Post.objects.exclude(removed = True).get(pk = post_id)
    from django.conf import settings
    paginator = ExtendedPaginator(Post.objects.filter(removed = False, thread = startpost.thread).exclude(pk = startpost.pk), 
        settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])

    return { 'startpost': startpost, 'thread': paginator.page(page), 'comment_form': PostForm() }

@rr('blog/post_print.html')
def print_post(request, post_id):
    return {'startpost': Post.objects.exclude(removed = True).get(pk = post_id), 'site': Site.objects.get_current().domain}

def offset(request, root_id, offset_id):
    from django.conf import settings
    paginator = Paginator(Post.objects.filter(thread__pk = root_id).exclude(pk = root_id), settings.PAGE_LIMITATIONS["FORUM_COMMENTS"])

    post = Post.objects.get(pk=offset_id)

    for page in paginator.page_range:
        if post in paginator.page(page).object_list:
            return HttpResponseRedirect("%s?offset=%s#post_%s" % (reverse("forum.views.thread", args = [root_id]), page, offset_id))

    raise Http404


