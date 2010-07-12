# -*- coding: utf-8 -*-

from django import template
from django.utils.html import linebreaks
from taverna.parsers.engines.phpBB.postmarkup import render_bbcode
import markdown
import string

from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

register = template.Library()

@register.filter
@stringfilter
def markup(value, parser):

    if parser == 1:
        value = render_bbcode(value)
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
def strippost(value, post):
    if len(value) > 382:
        value = value[:382]
        value = markup(value, post.parser)
        value = value + " ... <p>>>> <a href='%s'>%s</a></p>" % (reverse('blog.views.post_view', args=[post.id]), _("Read full post"))
    else:
        value = markup(value, post.parser)
    return value

@register.filter
def pg(value, paginator):
    for page in paginator.page_range:
        if value in paginator.page(page).object_list:
            return page

    return 0;
