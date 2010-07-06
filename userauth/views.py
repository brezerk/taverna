# -*- coding: utf-8 -*-
# Create your views here.

#from librecaptcha import librecaptcha
from recaptcha.client import captcha
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import forms

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from userauth.models import Profile
from blogs.models import Blog
from util import rr, getViewURL, getOpenIDStore

from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.conf import settings

from hashlib import md5

from openid.store import filestore
from openid.consumer import consumer

from django.template.defaultfilters import slugify

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required()
@rr ('userauth/profile.html')
def viewProfile(request, userid):
    try:
        user_info = User.objects.get(id__exact=userid)
        user_profile = Profile.objects.get(user=user_info)
        try:
            user_blog = Blog.objects.get(owner=user_info)
        except Blog.DoesNotExist:
            user_blog = None
        return {'user_info': user_info,
                'user_profile': user_profile,
                'user_blog': user_blog}

    except (User.DoesNotExist, Profile.DoesNotExist):
        return HttpResponseRedirect('/')

@login_required()
@rr ('userauth/settings.html')
def editProfile(request):

    profile = request.user.get_profile()

    class SettingsForm(forms.ModelForm):
        class Meta:
            model = Profile
            if profile.visible_name:
                exclude = ('user', 'openid_hash', 'photo', 'visible_name')
            else:
                exclude = ('user', 'openid_hash', 'photo')

        def save(self, **args):
            profile = super(SettingsForm, self).save(commit = False, **args)
            if request.POST['email']:
                mailhash = md5(request.POST['email']).hexdigest()
                profile.photo = mailhash
            profile.save()

    class UserSettingsForm(forms.ModelForm):
        class Meta:
            model = User
            exclude = ('username', 'password', 'is_staff',
                       'is_active', 'is_superuser', 'groups',
                       'user_permissions', 'last_login', 'date_joined')

    if request.method == 'POST':
        formProfile = SettingsForm(request.POST, instance=profile)
        formUser = UserSettingsForm(request.POST, instance=request.user)
        if formUser.is_valid() and formProfile.is_valid():
            formUser.save()
            formProfile.save()
            return HttpResponseRedirect(reverse("userauth.views.viewProfile",
                                        args=[request.user.id]))
    else:
        formProfile = SettingsForm(instance=profile)
        formUser = UserSettingsForm(instance=request.user)
    return {'formProfile': formProfile, 'formUser': formUser}

@rr ('userauth/openid.html')
def openidChalange(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    class OpenidForm(forms.Form):
        openid = forms.CharField(required=True, max_length=32)

    form = None

    if (request.POST):
        form = OpenidForm(request.POST)

        store = getOpenIDStore("/tmp/taverna_openid", "c_")
        c = consumer.Consumer(request.session, store)
        openid_url = request.POST['openid']

        try:
            auth_request = c.begin(openid_url)
        except consumer.DiscoveryFailure, exc:
            error = "OpenID discovery error: %s" % str(exc)
            return {'form': form, 'error': error}

        if auth_request.shouldSendRedirect():
            trust_root = getViewURL(request, openidChalange)
            redirect_to = getViewURL(request, openidFinish)
            return HttpResponseRedirect(auth_request.redirectURL(trust_root, redirect_to))
    else:
        form = OpenidForm()
    return {'form': form}

@rr ('userauth/openid.html')
def openidFinish(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    form = None
    error = None
    request_args = request.GET

    store = getOpenIDStore("/tmp/taverna_openid", "c_")
    c = consumer.Consumer(request.session, store)

    return_to = getViewURL(request, openidFinish)
    response = c.complete(request_args, return_to)

    if response.status == consumer.SUCCESS:
        openid_hash=md5(response.getDisplayIdentifier()).hexdigest()

        try:
            profile = Profile.objects.get(openid_hash = openid_hash)
            username = profile.user.username
            password = profile.user.password
            user = authenticate(username=username)
            if user is not None:
                login(request, user)
        except Profile.DoesNotExist:
            user = User(username = slugify(response.getDisplayIdentifier()[7:-1]),
                        is_staff = False, is_active = True,
                        is_superuser = False)
            user.save()
            profile = Profile(user = user, photo = "", openid_hash = openid_hash)
            profile.save()
            try:
                blog = Blog.objects.get(owner = user)
            except Blog.DoesNotExist:
                blog = Blog(owner = user)
                blog.save()

            auth = authenticate(username=user.username)
            if user is not None:
                login(request, auth)

        return HttpResponseRedirect(reverse("userauth.views.editProfile"))
    else:
        error = "Verification of %s failed: %s" % (response.getDisplayIdentifier(), response.message)

    return {'from': form, 'error': error}

