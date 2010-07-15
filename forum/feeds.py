from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from taverna.forum.models import Forum, Post
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from taverna.parsers.templatetags.markup import markup

from django.core.paginator import Paginator

class RssForum(Feed):
    link = ""
    description = ""
    title = ""

    def get_object(self, request, forum_id):
        return get_object_or_404(Forum, pk=forum_id)

    def items(self, obj):
        self.title =  _("Last 30 topics in \"%s\" forum" % (obj.name))
        self.description = obj.description
        self.link = obj.get_absolute_url()
        return Post.objects.filter(forum=obj, reply_to = None).order_by('-created')[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markup(item.text, item.parser)

class AtomForum(RssForum):
    feed_type = Atom1Feed
    subtitle = RssForum.description


class RssComments(Feed):
    link = ""
    description = ""
    title = ""

    paginator = None

    def get_object(self, request, post_id):
        return get_object_or_404(Post, pk=post_id)

    def items(self, obj):
        self.title = obj.title
        self.description = markup(obj.text, obj.parser)

        thread_list = Post.objects.filter(thread = obj.thread).exclude(pk = obj.pk)

        self.paginator = Paginator(thread_list, 10)


        return thread_list.order_by('-created')[:10]

    def item_title(self, item):
        if item.title:
            return item.title
        else:
            return item.thread.title

    def item_description(self, item):
        return item.text

    def item_link(self, item):
        for page in self.paginator.page_range:
            if item in self.paginator.page(page).object_list:
                return "%s?offset=%s#post_%s" % (reverse("forum.views.thread", args=[item.thread.pk]), page, item.pk)

        return reverse("blog.views.view", args=[item.blog.pk])

class AtomComments(RssComments):
    feed_type = Atom1Feed
    subtitle = RssComments.description

