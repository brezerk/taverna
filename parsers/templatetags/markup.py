# -*- coding: utf-8 -*-

from django import template
from django.utils.html import linebreaks
from taverna.parsers.engines.phpBB.postmarkup import render_bbcode
import markdown
import string

from django.template.defaultfilters import stringfilter
from taverna.parsers.models import Installed
from django.utils.html import conditional_escape


register = template.Library()

@register.filter
@stringfilter
def markup(value, parser):

    if parser:
        if parser.function == "render_bbcode":
            value = render_bbcode(value)
            return value
        elif parser.function == "markdown":
            value = markdown.markdown(value)
            return value

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
        value = value + "<a href='/blogs/tag/" + tag + "'>" + tag + "</a>"
    return value

@register.filter
def strippost(value, post):
    if len(value) > 382:
        value = value[:382]
        value = markup(value, post.parser_id)
        value = value + u" ... <p>>>> <a href='/" + post.owner_id.username + "/" + str(post.id) + u"'>Читать далее</a></p> "
    else:
        value = markup(value, post.parser_id)
    return value
