from django.conf.urls.defaults import *
from django.conf import settings
from django.core.urlresolvers import reverse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from taverna.blog.feeds import RssBlogTraker, AtomBlogTraker, RssBlog, AtomBlog
from taverna.blog.sitemaps import BlogSitemap
from taverna.forum.feeds import RssForum, AtomForum, RssComments, AtomComments
from taverna.userauth.feeds import RssUser, AtomUser

admin.autodiscover()


sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    (r'^libthread-(?P<post_id>\d+).so$', 'forum.views.thread'),
    (r'^libcups-(?P<post_id>\d+).so$', 'forum.views.print_post'),

    (r'^$', 'blog.views.index'),

    (r'^blog/libblog-(?P<blog_id>\d+).so$', 'blog.views.view'),
    (r'^blog/all/libblog-(?P<user_id>\d+).so$', 'blog.views.view_all'),

    (r'^blog/libdiff-(?P<diff_id>\d+).so$', 'forum.views.post_diff'),
    (r'^blog/librollback-(?P<diff_id>\d+).so$', 'forum.views.post_rollback'),

    url(r'^librss-0.so$', RssBlogTraker(), name='rss_blog_traker'),
    url(r'^libatom-0.so$', AtomBlogTraker(), name='atom_blog_traker'),
    (r'^blogs/$', 'blog.views.list'),
    (r'^blogs/public/$', 'blog.views.list_public'),
    (r'^blogs/usr/libblog.so$', 'blog.views.list_users'),
    (r'^blog/libpost-new.so$', 'blog.views.post_add'),
    (r'^blog/libpost-edit-(?P<post_id>\d+).so$', 'blog.views.post_edit'),
    (r'^blog/libsettings.so$', 'blog.views.settings'),
    (r'^blog/libtag-(?P<tag_id>\d+).so$', 'blog.views.tags_search'),

    (r'^forum.so$', 'forum.views.index'),
    (r'^forum-(?P<forum_id>\d+).so$', 'forum.views.forum'),

    url(r'^forum/librss-(?P<forum_id>\d+).so$', RssForum(), name='rss_forum_traker'),
    url(r'^forum/libatom-(?P<forum_id>\d+).so$', AtomForum(), name='atom_forum_traker'),

    (r'^forum/posting.so$', 'forum.views.reply'),
    (r'^libreply.so.(?P<post_id>\d+)$', 'forum.views.reply'),

    url(r'^thread/librss-(?P<post_id>\d+).so$', RssComments(), name='rss_comments'),
    url(r'^thread/libatom-(?P<post_id>\d+).so$', AtomComments(), name='atom_comments'),

    (r'^forum/createtopic.(?P<forum_id>\d+).so$', 'forum.views.topic_create'),
    (r'^forum/edittopic.(?P<topic_id>\d+).so$', 'forum.views.topic_edit'),
    (r'^forum/createforum.so$', 'forum.views.forum_create'),
    (r'^forum/tagsearch.so/(?P<tag_name>.*)$', 'forum.views.tags_search'),

    (r'^liboffset-(?P<root_id>\d+).so.(?P<offset_id>.*)$', 'forum.views.offset'),
    (r'^libremove-(?P<post_id>\d+).so$', 'forum.views.remove'),
    (r'^libview-(?P<post_id>\d+).so$', 'forum.views.post_view'),

    (r'^pam/liblogout.so$', 'userauth.views.openid_logout'),
    (r'^pam/libprofile-(?P<user_id>\d+).so$', 'userauth.views.profile_view'),
    (r'^pam/libprofile-edit.so$', 'userauth.views.profile_edit'),
    (r'^pam/libcomments-(?P<user_id>\d+).so$', 'userauth.views.user_comments'),
    (r'^pam/libnotify.so$', 'userauth.views.notify'),

    (r'^pam/librewards.so$', 'userauth.views.rewards'),

    (r'^libajax-(?P<post_id>\d+)-(?P<positive>\d+).so$', 'blog.views.vote_async'),
    (r'^blog/libvote-(?P<post_id>\d+)-(?P<positive>\d+).so$', 'blog.views.vote_generic'),

    url(r'^pam/librss-(?P<user_id>\d+).so$', RssUser(), name='rss_user'),
    url(r'^pam/libatom-(?P<user_id>\d+).so$', AtomUser(), name='atom_user'),

    (r'^login/$', 'userauth.views.openid_chalange'),
    (r'^login/finish/$', 'userauth.views.openid_finish'),

    url(r'^blog/librss-(?P<blog_id>\d+).so$', RssBlog(), name='rss_blog'),
    url(r'^blog/libatom-(?P<blog_id>\d+).so$', AtomBlog(), name='atom_blog'),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login/"
