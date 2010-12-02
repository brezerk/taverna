# -*- coding: utf-8 -*-

# Copyright (C) 2010 by Alexey S. Malakhov <brezerk@gmail.com>
#                       Opium <opium@jabber.com.ua>
#
# This file is part of Taverna
#
# Taverna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Taverna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Taverna.  If not, see <http://www.gnu.org/licenses/>.

# Create your views here.

from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms import Form, ModelForm, CharField
from django.forms import ModelChoiceField, ValidationError

from django.utils.datastructures import MultiValueDictKeyError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from userauth.models import Profile, ReasonList
from blog.models import Blog
from forum.models import Post, PostVote

from util import rr, getViewURL, getOpenIDStore

from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.conf import settings

from hashlib import sha512, md5

from openid.store import filestore
from openid.consumer import consumer
from openid.extensions import sreg

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.defaultfilters import slugify

from django.http import Http404

from django.db.models import Q
from django.shortcuts import get_object_or_404

def openid_logout(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required()
@rr ('userauth/profile.html')
def profile_view(request, user_id=None):
    if user_id:
        user_info = get_object_or_404(User, pk=user_id)
    else:
        user_info = request.user

    user_blog = Blog.objects.filter(owner=user_info)[:1][0]
    print user_blog
    print user_blog.id

    return {
        'user_info': user_info,
        'user_blog': user_blog
    }

@login_required()
@rr ('userauth/settings.html')
def profile_edit(request):
    from blog.views import error

    if not request.user.profile.can_edit_profile():
        return error(request, "PROFILE_EDIT")

    profile = request.user.get_profile()

    class SettingsForm(ModelForm):
        class Meta:
            model = Profile
            if profile.visible_name:
                exclude = (
                    'user',
                    'karma',
                    'photo',
                    'visible_name',
                    'force',
                )
            else:
                exclude = (
                    'user',
                    'karma',
                    'photo',
                    'force',
                )

        def save(self, **args):
            profile = super(SettingsForm, self).save(commit=False, **args)
            if request.POST['email']:
                mailhash = md5(request.POST['email']).hexdigest()
                profile.photo = mailhash
            profile.save()

            request.user.profile.use_force("PROFILE_EDIT")
            request.user.profile.save()

            try:
                q = self.cleaned_data["visible_name"]
            except KeyError:
                pass
            else:
                blog = Blog.objects.filter(owner=request.user.id)[:1]
                blog.name = profile.visible_name
                blog.save()

    class UserSettingsForm(ModelForm):
        class Meta:
            model = User
            exclude = (
                'username',
                'password',
                'is_staff',
                'is_active',
                'is_superuser',
                'groups',
                'user_permissions',
                'last_login',
                'date_joined'
            )

    if request.method == 'POST':
        formProfile = SettingsForm(request.POST, instance=profile)
        formUser = UserSettingsForm(request.POST, instance=request.user)
        if formUser.is_valid() and formProfile.is_valid():
            formUser.save()
            formProfile.save()
            return HttpResponseRedirect(
                       reverse(
                           "userauth.views.profile_view",
                           args=[request.user.id]
                       )
                   )
    else:
        formProfile = SettingsForm(instance=profile)
        formUser = UserSettingsForm(instance=request.user)
    return {'formProfile': formProfile, 'formUser': formUser}

@rr ('userauth/openid.html')
def openid_chalange(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    class OpenidForm(Form):
        openid = CharField(required=True, max_length=32)

        def clean_openid(self):
            openid = self.cleaned_data['openid']
            import re
            p = re.compile('^[a-zA-Z._-]+$')
            if not p.match(openid):
                raise ValidationError(_("Invalid openid string."))

    form = None

    if (request.POST):
        form = OpenidForm(request.POST)

        if form.is_valid():
            store = getOpenIDStore("/tmp/taverna_openid", "c_")
            c = consumer.Consumer(request.session, store)
            openid_url = request.POST['openid']


            # Google ...
            if openid_url == "google":
                openid_url = 'https://www.google.com/accounts/o8/id'
            try:
                auth_request = c.begin(openid_url)
            except consumer.DiscoveryFailure, exc:
                error = "OpenID discovery error: %s" % str(exc)
                return {'form': form, 'error': error}

            trust_root = getViewURL(request, openid_chalange)
            redirect_to = getViewURL(request, openid_finish)
            return HttpResponseRedirect(
                       auth_request.redirectURL(trust_root, redirect_to)
                   )
    else:
        form = OpenidForm()
    return {'form': form}

@rr ('userauth/openid.html')
def openid_finish(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    form = None
    error = None
    request_args = request.GET

    store = getOpenIDStore("/tmp/taverna_openid", "c_")
    c = consumer.Consumer(request.session, store)

    return_to = getViewURL(request, openid_finish)
    response = c.complete(request_args, return_to)

    if response.status == consumer.SUCCESS:
        openid_hash=sha512(response.getDisplayIdentifier()).hexdigest()
        sreg_response = sreg.SRegResponse.fromSuccessResponse(response)

        try:
            profile = Profile.objects.get(openid_hash=openid_hash)
            username = profile.user.username
            user = authenticate(username=username)
            if user is not None:
                login(request, user)

            return HttpResponseRedirect("/")
        except Profile.DoesNotExist:
            user = User(
                       username=openid_hash[:30],
                       is_staff=False,
                       is_active=True,
                       is_superuser=False
                   )
            user.save()
            profile = Profile(
                          user=user,
                          photo="",
                          openid_hash=openid_hash,
                          karma=settings.START_RATING,
                          force=settings.START_RATING
                      )
            profile.save()
            try:
                blog = Blog.objects.get(owner=user)
            except Blog.DoesNotExist:
                blog = Blog(owner=user, name=openid_hash[:30])
                blog.save()

            auth = authenticate(username=user.username)
            if user is not None:
                login(request, auth)

            return HttpResponseRedirect(
                       reverse("userauth.views.profile_edit")
                   )
    else:
        error = "Verification of %s failed: %s" % (
                    response.getDisplayIdentifier(),
                    response.message
                )

    return {'from': form, 'error': error}

@login_required()
@rr("userauth/coments.html")
def user_comments(request, user_id):
    user_info = User.objects.get(pk=user_id)

    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    paginator = Paginator(
                    Post.objects.filter(
                        owner=user_info,
                        forum=None,
                        blog=None
                    ).order_by('-created'),
                    settings.PAGE_LIMITATIONS["FORUM_TOPICS"]
                )
    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return {
        'thread': thread,
        'user_info': user_info,
        'request_url': request.get_full_path()
    }

@login_required()
@rr("userauth/notifyes.html")
def notify(request):
    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    paginator = Paginator(
                    Post.objects.exclude(owner=request.user) \
                    .filter(
                        forum=None,
                        blog=None,
                        reply_to__owner=request.user
                    ).order_by('-created') \
                    .select_related(
                        'owner__profile',
                        'reply_to__owner__profile',
                        'thread__blog',
                        'thread__forum'
                    ), settings.PAGE_LIMITATIONS["FORUM_TOPICS"]
                )

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return {
        'thread': thread,
        'request_url': request.get_full_path()
    }

@login_required()
@rr("userauth/scourges.html")
def scourges(request, user_id):
    user_info = User.objects.get(pk=user_id)
    form = None

    if not request.user.is_staff:
        if request.user != user_info:
            raise Http404
    else:
        class SettingsForm(ModelForm):
            class Meta:
                model = User
                fields = ('is_active',)

            def save(self, **args):
                user = super(SettingsForm, self).save(commit=False, **args)
                user.save()

        if request.method == 'POST':
            form = SettingsForm(request.POST, instance=user_info)
            if form.is_valid():
                form.save()
        else:
            form = SettingsForm(instance=user_info)
    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    paginator = Paginator(
                    PostVote.objects.exclude(reason=None) \
                    .filter(post__owner=user_info).order_by('-pk'),
                    settings.PAGE_LIMITATIONS["FORUM_TOPICS"]
                )

    try:
        rewards = paginator.page(page)
    except (EmptyPage, InvalidPage):
        rewards = paginator.page(paginator.num_pages)

    return {
        'rewards': rewards,
        'request_url': request.get_full_path(),
        'user_info': user_info,
        'form': form
    }

@rr("userauth/graveyard.html")
def graveyard(request):
    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    paginator = Paginator(
                    Profile.objects.filter(karma__lt=0) \
                    .exclude(user__is_active=0).order_by('-karma') \
                    .select_related('user'),
                    settings.PAGE_LIMITATIONS["FORUM_TOPICS"]
                )

    try:
        users = paginator.page(page)
    except (EmptyPage, InvalidPage):
        users = paginator.page(paginator.num_pages)

    return {'users': users, 'request_url': request.get_full_path()}

