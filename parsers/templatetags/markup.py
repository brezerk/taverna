# -*- coding: utf-8 -*-

from django import template
from django.utils.html import linebreaks
from taverna.parsers.engines.phpBB.postmarkup import render_bbcode
import markdown
import string
import re

from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

register = template.Library()

@register.filter
@stringfilter
def markup(value, parser):

    if parser == 1:
        value = "<p>" + render_bbcode(value) + "</p>"
        return value
    elif parser == 2:
        value = markdown.markdown(value)
        return value
    else:
        esc = conditional_escape
        value = esc(value)
        value = linebreaks(value)
    return value

@register.filter
@stringfilter
def tags(value):
    tag_list = value.split(", ")
    value = ""

    first = True

    for tag in tag_list:
        if first:
            first = False
        else:
            value = value + ", "
        value = value + "<a href='/'>" + tag + "</a>"
    return value

@register.filter
def forumtags(value):
    tag_list = re.split('\[(.*?)\]', value.title)
    tag_string = ""
    for tag in tag_list:
        if tag:
           if tag != tag_list[-1]:
               tag_string = tag_string + u"[<a href='/forum/tagsearch-0.so/%s'>%s</a>]" % (tag, tag)

    tag_string = tag_string + u"<a href='%s'>%s</a>" % (reverse('forum.views.thread', args=[value.pk]), tag_list[-1])
    return tag_string

@register.filter
def strippost(value, post):
    if len(value) > 382:
        value = value[:382]
        value = markup(value, post.parser)
        value = value + " ... <p>>>> <a href='%s'>%s</a></p>" % (reverse('forum.views.thread', args=[post.pk]), _("Read full post"))
    else:
        value = markup(value, post.parser)
    return value

@register.filter
def pg(value, paginator):
    for page in paginator.page_range:
        if value in paginator.page(page).object_list:
            return page

    return 0;
