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

#from librecaptcha import librecaptcha
#from recaptcha.client import captcha
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms import Form, ModelForm, CharField

from django.utils.datastructures import MultiValueDictKeyError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from userauth.models import Profile
from blog.models import Blog
from forum.models import Post, PostVote

from util import rr, getViewURL, getOpenIDStore

from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.conf import settings

from hashlib import sha512, md5

from openid.store import filestore
from openid.consumer import consumer
from openid import sreg

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.defaultfilters import slugify

from django.http import Http404

from django.db.models import Q

def openid_logout(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required()
@rr ('userauth/profile.html')
def profile_view(request, user_id):
    user_info = User.objects.get(pk = user_id)

    try:
        user_blog = Blog.objects.get(owner = user_info)
    except:
        user_blog = ""

    return {'user_info': user_info,'user_blog': user_blog}

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
                exclude = ('user', 'karma', 'photo', 'visible_name', 'force', 'buryed', 'buryed_reason')
            else:
                exclude = ('user', 'karma', 'photo', 'force', 'buryed', 'buryed_reason')

        def save(self, **args):
            profile = super(SettingsForm, self).save(commit = False, **args)
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
                blog = Blog.objects.get(owner = request.user.id)
                blog.name = profile.visible_name
                blog.save()

    class UserSettingsForm(ModelForm):
        class Meta:
            model = User
            exclude = ('username', 'password', 'is_staff',
                       'is_active', 'is_superuser', 'groups',
                       'user_permissions', 'last_login', 'date_joined')

    if request.method == 'POST':
        formProfile = SettingsForm(request.POST, instance = profile)
        formUser = UserSettingsForm(request.POST, instance = request.user)
        if formUser.is_valid() and formProfile.is_valid():
            formUser.save()
            formProfile.save()
            return HttpResponseRedirect(reverse("userauth.views.profile_view",
                                        args = [request.user.id]))
    else:
        formProfile = SettingsForm(instance = profile)
        formUser = UserSettingsForm(instance = request.user)
    return {'formProfile': formProfile, 'formUser': formUser}

@rr ('userauth/openid.html')
def openid_chalange(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    class OpenidForm(Form):
        openid = CharField(required = True, max_length = 32)

    form = None

    if (request.POST):
        form = OpenidForm(request.POST)

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

#       import openid.extensions.ax as ax
#       ax_request = ax.FetchRequest()
#       ax_request.add (ax.AttrInfo ('http://schema.openid.net/contact/email', alias='email', required=False))
#       ax_request.add (ax.AttrInfo ('http://axschema.org/namePerson/first', alias='firstname', required=False))
#       auth_request.addExtension(ax_request)

#       if auth_request.shouldSendRedirect():
        trust_root = getViewURL(request, openid_chalange)
        redirect_to = getViewURL(request, openid_finish)
        return HttpResponseRedirect(auth_request.redirectURL(trust_root, redirect_to))
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

#       import openid.extensions.ax as ax
#       ax_response = ax.FetchResponse.fromSuccessResponse(response)

#       print ax_response
#
#       ax_items = ""

#       if ax_response:
#           ax_items = {
#               'email': ax_response.get('http://schema.openid.net/contact/email'),
#               'firstname': ax_response.get('http://axschema.org/namePerson/first'),
#           }
#
#       print ax_items

        try:
            profile = Profile.objects.get(openid_hash = openid_hash)
            username = profile.user.username
            user = authenticate(username=username)
            if user is not None:
                login(request, user)

            return HttpResponseRedirect("/")
        except Profile.DoesNotExist:
            user = User(username = openid_hash[:30], is_staff = False, is_active = True,
                        is_superuser = False)
            user.save()
            profile = Profile(user = user, photo = "", openid_hash = openid_hash)
            profile.save()
            try:
                blog = Blog.objects.get(owner = user)
            except Blog.DoesNotExist:
                blog = Blog(owner = user, name = openid_hash[:30])
                blog.save()

            auth = authenticate(username=user.username)
            if user is not None:
                login(request, auth)

            return HttpResponseRedirect(reverse("userauth.views.profile_edit"))
    else:
        error = "Verification of %s failed: %s" % (response.getDisplayIdentifier(), response.message)

    return {'from': form, 'error': error}

@rr("userauth/coments.html")
def user_comments(request, user_id):
    user_info = User.objects.get(pk = user_id)

    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    from django.conf import settings
    paginator = Paginator(Post.objects.filter(removed = False, owner = user_info, forum = None,
                          blog = None).order_by('-created'),
                          settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return {'thread': thread, 'user_info': user_info, 'request_url': request.get_full_path()}

@rr("userauth/coments.html")
def notify(request):
    user_info = request.user

    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    from django.conf import settings
    paginator = Paginator(Post.objects.exclude(owner=user_info).filter(removed = False, reply_to__owner = user_info,
                          forum = None, blog = None).order_by('-created'), settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return {'thread': thread, 'request_url': request.get_full_path()}

@rr("userauth/rewards.html")
def rewards(request, user_id):
    user_info = User.objects.get(pk = user_id)

    if not request.user.is_staff:
        if request.user != user_info:
            raise Http404

    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    from django.conf import settings
    paginator = Paginator(PostVote.objects.exclude(reason = None).filter(post__owner = user_info).order_by('-pk'), settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        rewards = paginator.page(page)
    except (EmptyPage, InvalidPage):
        rewards = paginator.page(paginator.num_pages)

    return {'rewards': rewards, 'request_url': request.get_full_path(), 'user_info': user_info}

@rr("userauth/graveyard.html")
def graveyard(request):
    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    from django.conf import settings
    paginator = Paginator(Profile.objects.filter(Q(karma__lt = 0) | Q(buryed = True)).order_by('-buryed'), settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        users = paginator.page(page)
    except (EmptyPage, InvalidPage):
        users = paginator.page(paginator.num_pages)

    return {'users': users, 'request_url': request.get_full_path()}

