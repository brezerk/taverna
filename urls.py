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
    (r'^blog/libblog-(?P<page>\d+).so$', 'blogs.views.index'),

    (r'^blog/libblog-0.so.(?P<blog_id>\d+)$', 'blogs.views.view'),
    (r'^blog/libblog-(?P<page>\d+).so.(?P<blog_id>\d+)$', 'blogs.views.view'),

    url(r'^librss-0.so$', RssBlogTraker(), name='rss_blog_traker'),
    url(r'^libatom-0.so$', AtomBlogTraker(), name='atom_blog_traker'),
    (r'^blogs/$', 'blogs.views.list'),
    (r'^blogs/public/$', 'blogs.views.list_public'),
    (r'^blogs/users/$', 'blogs.views.list_users'),
    (r'^blog/libpost-new-1.so$', 'blogs.views.post_add'),
    (r'^blog/libsettings-0.so$', 'blogs.views.settings'),
    (r'^blog/libpost-0.so.(?P<post_id>\d+)$', 'blogs.views.post_view'),
    (r'^blog/libtag-0.so.(?P<tag_id>\d+)$', 'blogs.views.tags_search'),
    (r'^blog/libtag-(?P<page>\d+).so.(?P<tag_id>\d+)$', 'blogs.views.tags_search'),
    (r'^blog/libcomment.so.(?P<post_id>\d+)$', 'blogs.views.post_comment'),

    (r'^forum.so$', 'forum.views.index'),
    (r'^forum.so.(?P<forum_id>\d+)$', 'forum.views.forum'),
    (r'^forum/posting.so$', 'forum.views.reply'),
    (r'^forum/reply.so.(?P<post_id>\d+)$', 'forum.views.reply'),
    (r'^forum/thread.so.(?P<post_id>\d+)$', 'forum.views.thread'),
    (r'^forum/createtopic.so.(?P<forum_id>\d+)$', 'forum.views.topic_create'),
    (r'^forum/createforum.so$', 'forum.views.forum_create'),

    (r'^pam/liblogout.so$', 'userauth.views.openid_logout'),
    (r'^pam/libprofile-0.so.(?P<user_id>\d+)$', 'userauth.views.profile_view'),
    (r'^pam/libprofile-edit-0.so$', 'userauth.views.profile_edit'),

    (r'^login/$', 'userauth.views.openid_chalange'),
    (r'^login/finish/$', 'userauth.views.openid_finish'),

    url(r'^blog/librss-0.so.(?P<blog_id>\d+)$', RssBlog(), name='rss_blog'),
    url(r'^blog/libatom-0.so.(?P<blog_id>\d+)$', AtomBlog(), name='atom_blog'),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login/"
