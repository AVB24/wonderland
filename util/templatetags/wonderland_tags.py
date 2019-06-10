import math, datetime
from django import template
from django.conf import settings
from wagtail.search.backends import get_search_backend

register = template.Library()

@register.filter
def convertTime(time):
    hrs = math.floor(time / 3600)
    mins = math.floor((time %3600)/60)
    secs = time % 60

    ret = ""
    if hrs > 0:
        ret += str(hrs) + ":" + ("0" if mins < 10 else "")
    
    ret += "" + str(mins) + ":" + ("0" if secs < 10 else "")
    ret += "" + format(secs, '.3f')
    return ret

@register.filter
def datetime_filter(dttm):
    return dttm.strftime("%Y-%m-%d")

@register.simple_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page

@register.simple_tag(takes_context=True)
def get_site(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site


# Retrieves the top menu items - the immediate children of the parent page
@register.inclusion_tag('util/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    request = context['request']
    if request.user.is_authenticated:
        menuitems = parent.get_children().live().in_menu()
    else:
        menuitems = parent.get_children().live().in_menu().public()
    for menuitem in menuitems:
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menuitem.active = (calling_page.url.startswith(menuitem.url)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }
