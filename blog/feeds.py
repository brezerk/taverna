from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from taverna.blog.models import Blog, Post, Tag
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from taverna.parsers.templatetags.markup import markup

from django.core.paginator import Paginator

class RssBlogTraker(Feed):
    title = _("Last 10 blogs topics")
    link = "/"
    description = _("Updates on changes and additions to blogs topics.")

    def items(self):
        return Post.objects.order_by('-created')[:10]

    def item_title(self, item):
        return "%s - %s" % (item.blog.name, item.title)

    def item_description(self, item):
        return markup(item.content, item.parser)

class AtomBlogTraker(RssBlogTraker):
   feed_type = Atom1Feed
   subtitle = RssBlogTraker.description

class RssBlog(Feed):
    link = ""
    description = ""
    title = ""

    def get_object(self, request, blog_id):
        return get_object_or_404(Blog, pk=blog_id)

    def items(self, obj):
        self.title =  _("Last 10 topics for \"%s\" blog" % (obj.name))
        self.description = obj.desc
        self.link = obj.get_absolute_url()
        return Post.objects.filter(blog=obj).order_by('-created')[:10]

    def item_title(self, item):
        return "%s - %s" % (item.blog.name, item.title)

    def item_description(self, item):
        return markup(item.content, item.parser)

class AtomBlog(RssBlog):
    feed_type = Atom1Feed
    subtitle = RssBlog.description

class RssBlogComments(Feed):
    link = ""
    description = ""
    title = ""

    paginator = None

    def get_object(self, request, post_id):
        return get_object_or_404(Post, pk=post_id)

    def items(self, obj):
        self.title = obj.title
        self.description = markup(obj.content, obj.parser)
        self.paginator = Paginator(obj.post_set.all(), 10)
        return obj.post_set.all().order_by('-created')[:10]

    def item_title(self, item):
        if item.title:
            return item.title
        else:
            return item.blog_post.title

    def item_description(self, item):
        return item.text

    def item_link(self, item):
        for page in self.paginator.page_range:
            if item in self.paginator.page(page).object_list:
                return "%s#post_%s" % (reverse("blog.views.post_view", args=[page, item.blog_post.pk]), item.pk)

        return reverse("blog.views.post_view", args=[item.blog_post.pk])

class AtomBlogComments(RssBlogComments):
    feed_type = Atom1Feed
    subtitle = RssBlogComments.description
