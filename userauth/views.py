# -*- coding: utf-8 -*-
# Create your views here.

#from librecaptcha import librecaptcha
from recaptcha.client import captcha
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

def openid_logout(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required()
@rr ('userauth/profile.html')
def profile_view(request, user_id):
    try:
        user_info = User.objects.get(pk = user_id)
        try:
            user_blog = Blog.objects.get(owner = user_info)
        except Blog.DoesNotExist:
            user_blog = None
        return {'user_info': user_info,
                'user_blog': user_blog}

    except (User.DoesNotExist, Profile.DoesNotExist):
        return HttpResponseRedirect('/')

@login_required()
@rr ('userauth/settings.html')
def profile_edit(request):

    profile = request.user.get_profile()

    class SettingsForm(ModelForm):
        class Meta:
            model = Profile
            if profile.visible_name:
                exclude = ('karma', 'photo', 'visible_name')
            else:
                exclude = ('karma', 'photo')

        def save(self, **args):
            profile = super(SettingsForm, self).save(commit = False, **args)
            if request.POST['email']:
                mailhash = md5(request.POST['email']).hexdigest()
                profile.photo = mailhash
            profile.save()

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
    paginator = Paginator(Post.objects.filter(owner = user_info, forum = None,
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
    paginator = Paginator(Post.objects.exclude(owner=user_info).filter(reply_to__owner = user_info,
                          forum = None, blog = None).order_by('-created'), settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return {'thread': thread, 'request_url': request.get_full_path()}

@rr("userauth/coments.html")
def karma(request):
    user_info = request.user

    try:
        page = int(request.GET['offset'])
    except (MultiValueDictKeyError, TypeError):
        page = 1

    from django.conf import settings
    paginator = Paginator(PostVote.objects.exclude(reason = None).order_by('-pk'), settings.PAGE_LIMITATIONS["FORUM_TOPICS"])

    try:
        thread = paginator.page(page)
    except (EmptyPage, InvalidPage):
        thread = paginator.page(paginator.num_pages)

    return {'thread': thread, 'request_url': request.get_full_path()}

