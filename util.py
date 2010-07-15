from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse as reverseURL
from urlparse import urljoin

from django.db import connection
from django.conf import settings
from openid.store.filestore import FileOpenIDStore
from openid.store import sqlstore
from django.core.paginator import Paginator

class ExtendedPaginator(Paginator):

    page_range = None
    show_first = False
    show_last = False

    def page(self, number):
        number = int(number)
        if self.num_pages < 5:
            self.page_range = range(1, self.num_pages + 1)
        if number > 5:
            start = number - 5
            self.show_first = True
        else:
            start = 1
        if number > self.num_pages - 5:
            end = self.num_pages
        else:
            end = number + 5
            self.show_last = True
        self.page_range = range(start, end)

        return Paginator.page(self, number)

def rr(template):
    def decor(view):
        def wrapper(request, *args, **kwargs):
            val = view(request, *args, **kwargs)
            if type(val) == type({}):
                val.update({'user': request.user})
                val.update(csrf(request))
                return render_to_response(template, val)
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

