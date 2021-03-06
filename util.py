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

from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse as reverseURL
from urlparse import urljoin

from django.db import connection
from django.conf import settings
from openid.store.filestore import FileOpenIDStore
from openid.store import sqlstore
from django.core.paginator import Paginator
from django.core.cache import cache

from userauth.models import Profile
from blog.models import Blog
from django.contrib.syndication.views import Feed


class ExtendedPaginator(Paginator):

    page_range = None

    def page(self, number):
        number = int(number)

        if self.num_pages < 10:
            self.page_range = range(1, self.num_pages + 1)

        start = number - 5
        end = number + 5

        if start <= 10:
            end = 10 if self.num_pages > 9 else self.num_pages
            start = 1
        elif end >= self.num_pages:
            start = self.num_pages - 10
            end = self.num_pages

        self.page_range = range(start, end + 1)

        return Paginator.page(self, number)

def clear_template_cache(key, *variables):
    from django.utils.http import urlquote
    from django.utils.hashcompat import md5_constructor

    args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
    cache_key = 'template.cache.%s.%s' % (key, args.hexdigest())
    if settings.DEBUG and cache.get(cache_key) is not None:
        print "Removed template cache %s" % (cache_key)
    else:
        print "Attempted to delete %s" % cache_key
    cache.delete(cache_key)


def invalidate_cache(post):
    from forum.feeds import RssForum, RssComments, RssTrackerFeed
    from blog.feeds import RssBlogFeed, RssBlog
    """
    Be carefull with invalidation! :]
    """

    RssTrackerFeed().clear_cache()

    if post.thread is None:
        return

    if post.forum is not None and post.thread != post.pk:
        # Invalidating forum tracker cache
        RssForum().clear_cache(forum_id = post.forum.pk)

    elif post.blog is not None:
        # Blog post was changed
        RssBlogFeed().clear_cache()
        RssBlog().clear_cache(blog_id = post.thread.blog.pk)
        # Invalidating post cache
        clear_template_cache("blogpost", post.pk)
    else:
        # Comment for blog/forum was added/changed:
        RssComments().clear_cache(post_id = post.thread.pk)

        if post.thread.blog is not None:
            # On new comment added we need invalidate start post cache
            clear_template_cache("blogpost", post.thread.pk)


def modify_rating(post, cost = 1, positive = False):
    from forum.models import Post
    from django.db.models import F
    if positive:
        Post.objects.filter(id = post.pk).update(rating = F("rating") + cost)
        Profile.objects.filter(id = post.owner.profile.pk).update(
            force = F("force") + cost, karma = F("karma") + cost
        )
    else:
        Post.objects.filter(id = post.pk).update(rating = F("rating") - cost)
        Profile.objects.filter(id = post.owner.profile.pk).update(
            force = F("force") - cost, karma = F("karma") - cost
        )
    invalidate_cache(post)

class CachedFeed(Feed):

    def clear_cache(self, *args, **kwargs):
        print "deleting "+ self.get_cache_key(*args, **kwargs)
        cache.delete(self.get_cache_key())

    def get_cache_key(self, *args, **kwargs):
        return self.cache_prefix + ".".join([str(x) for x in args]) \
            + ".".join([str(x) for x in kwargs.keys()]) \
            + ".".join([str(x) for x in kwargs.values()])

    def __call__(self, request, *args, **kwargs):
        key = self.get_cache_key(*args, **kwargs)
        reply = cache.get(key)
        if reply is None:
            reply = Feed.__call__(self, request, *args, **kwargs)
            cache.set(key, reply, 100500) # About 28 hours :]
            if settings.DEBUG:
                print "Cache %s miss!" % (key)

        else:
            if settings.DEBUG:
                print "Cache %s hit!" % (key)
        return reply

def rr(template, mimetype=None, templates={}):
    from django.template.loader import get_template
    from django.template import Context
    if template not in templates:
        templates[template] = get_template(template)

    def decor(view):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated():
                # This is an a fixup for root account
                try:
                    profile = request.user.profile
                except:
                    profile = Profile(
                        user=request.user,
                        photo="",
                        openid_hash="",
                        karma=settings.START_RATING,
                        force=settings.START_RATING
                    )
                    profile.save()

                    try:
                        blog = Blog.objects.get(owner=request.user)
                    except Blog.DoesNotExist:
                        blog = Blog(owner=request.user, name=request.user.username)
                        blog.save()
                    except:
                        pass

                if not profile.visible_name:
                    if request.path not in (reverseURL("userauth.views.profile_edit"), 
                            reverseURL("userauth.views.openid_logout")):
                        return redirect("userauth.views.profile_edit")
            val = view(request, *args, **kwargs)
            if type(val) == type({}):
                val.update({'user': request.user})
                val.update(csrf(request))

                if settings.TEMPLATE_DEBUG:
                    return render_to_response(template, val, mimetype=mimetype)

                return HttpResponse(templates[template].render(Context(val)), mimetype = mimetype)
            else:
                return val
        return wrapper
    return decor

def getViewURL(req, view_name_or_obj, args=None, kwargs=None):
    relative_url = reverseURL(view_name_or_obj, args=args, kwargs=kwargs)
    full_path = req.META.get('SCRIPT_NAME', '') + relative_url
    return urljoin(getBaseURL(req), full_path)

def getBaseURL(req):
    """
    Given a Django web request object, returns the OpenID 'trust root'
    for that request; namely, the absolute URL to the site root which
    is serving the Django request.  The trust root will include the
    proper scheme and authority.  It will lack a port if the port is
    standard (80, 443).
    """
    name = req.META['HTTP_HOST']
    try:
        name = name[:name.index(':')]
    except:
        pass

    try:
        port = int(req.META['SERVER_PORT'])
    except:
        port = 80

    proto = req.META['SERVER_PROTOCOL']

    if 'HTTPS' in proto:
        proto = 'https'
    else:
        proto = 'http'

    if port in [80, 443] or not port:
        port = ''
    else:
        port = ':%s' % (port,)

    url = "%s://%s%s/" % (proto, name, port)
    return url

def getOpenIDStore(filestore_path, table_prefix):
    """
    Returns an OpenID association store object based on the database
    engine chosen for this Django application.

    * If no database engine is chosen, a filesystem-based store will
      be used whose path is filestore_path.

    * If a database engine is chosen, a store object for that database
      type will be returned.

    * If the chosen engine is not supported by the OpenID library,
      raise ImproperlyConfigured.

    * If a database store is used, this will create the tables
      necessary to use it.  The table names will be prefixed with
      table_prefix.  DO NOT use the same table prefix for both an
      OpenID consumer and an OpenID server in the same database.

    The result of this function should be passed to the Consumer
    constructor as the store parameter.
    """
    if not settings.DATABASES:
        return FileOpenIDStore(filestore_path)

    # Possible side-effect: create a database connection if one isn't
    # already open.
    connection.cursor()

    # Create table names to specify for SQL-backed stores.
    tablenames = {
        'associations_table': table_prefix + 'openid_associations',
        'nonces_table': table_prefix + 'openid_nonces',
        }

    types = {
        'django.db.backends.postgresql': sqlstore.PostgreSQLStore,
        'django.db.backends.mysql': sqlstore.MySQLStore,
        'django.db.backends.sqlite3': sqlstore.SQLiteStore,
        }


    try:
        s = types[settings.DATABASES['default']['ENGINE']](connection.connection,
                                            **tablenames)
    except KeyError:
        raise ImproperlyConfigured, \
              "Database engine %s not supported by OpenID library" % \
              (settings.DATABASE_ENGINE,)

    try:
        s.createTables()
    except (SystemExit, KeyboardInterrupt, MemoryError), e:
        raise
    except:
        # XXX This is not the Right Way to do this, but because the
        # underlying database implementation might differ in behavior
        # at this point, we can't reliably catch the right
        # exception(s) here.  Ideally, the SQL store in the OpenID
        # library would catch exceptions that it expects and fail
        # silently, but that could be bad, too.  More ideally, the SQL
        # store would not attempt to create tables it knows already
        # exists.
	pass

    return s

