from django.conf.urls.defaults import *
from django.conf import settings
from django.core.urlresolvers import reverse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from taverna.blogs.feeds import RssBlogTraker, AtomBlogTraker, RssBlog, AtomBlog
from taverna.blogs.sitemaps import BlogSitemap

admin.autodiscover()


sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    (r'^$', 'blogs.views.index'),
    url(r'^librss-0.so$', RssBlogTraker(), name='rss_blog_traker'),
    url(r'^libatom-0.so$', AtomBlogTraker(), name='atom_blog_traker'),
    (r'^blogs/$', 'blogs.views.list'),
    (r'^blogs/public/$', 'blogs.views.list_public'),
    (r'^blogs/users/$', 'blogs.views.list_users'),
# FIXME: reserved for paginator;
#    (r'^blogs/users/(?P<page>\w+)/$', 'blogs.views.viewBlogsUserList'),
    (r'^blog/libpost-new-1.so$', 'blogs.views.post_add'),
    (r'^blog/libsettings-0.so$', 'blogs.views.settings'),
    (r'^blog/libpost-0.so.(?P<post_id>\d+)$', 'blogs.views.post_view'),
    (r'^blog/libtag-0.so.(?P<tag_id>\d+)$', 'blogs.views.tags_search'),

    (r'^libforum-1.so$', 'forum.views.index'),
    (r'^libforum-1/(?P<forum_id>\d+).so$', 'forum.views.forum'),
    (r'^libforum-1/posting.so$', 'forum.views.reply'),
    (r'^libforum-1/reply-(?P<post_id>\d+).so$', 'forum.views.reply'),
    (r'^libforum-1/thread-(?P<post_id>\d+).so$', 'forum.views.thread'),
    (r'^libforum-1/create.so$', 'forum.views.forum_create'),

    (r'^forums/$', 'forum.views.index'),
    (r'^forums/thread/(?P<post_id>\d+).html$', 'forum.views.thread'),
    (r'^forums/reply/(?P<forum_id>\d+).html$', 'forum.views.reply'),
    (r'^forums/thread/reply/(?P<post_id>\d+).html$', 'forum.views.reply'),
    (r'^forums/libforum-0.so.(?P<forum_id>\d+)$', 'forum.views.forum'),
    (r'^forum_create/$', 'forum.views.forum_create'),

    (r'^pam/liblogout.so$', 'userauth.views.openid_logout'),
    (r'^pam/libprofile-0.so.(?P<user_id>\d+)$', 'userauth.views.profile_view'),
    (r'^pam/libprofile-edit-0.so$', 'userauth.views.profile_edit'),

    (r'^login/$', 'userauth.views.openid_chalange'),
    (r'^login/finish/$', 'userauth.views.openid_finish'),

    (r'^blog/libblog-0.so.(?P<blog_id>\d+)$', 'blogs.views.view'), # WARNING: this one MUST be last
    url(r'^blog/librss-0.so.(?P<blog_id>\d+)$', RssBlog(), name='rss_blog'),
    url(r'^blog/libatom-0.so.(?P<blog_id>\d+)$', AtomBlog(), name='atom_blog'),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login/"
