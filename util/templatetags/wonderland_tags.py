from django import template
from django.conf import settings
from records.models import Lap
from wagtail.search.backends import get_search_backend

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page


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

@register.inclusion_tag('records/tags/lap_results.html', takes_context=True)
def get_laps(context, query, is_best):
    print("Hello")
    if query:
        s = get_search_backend()
        laps = s.search(query, Lap.objects.filter(best=is_best), operator="and")
    else:
        laps = Lap.objects.all().filter(best=is_best)

    return {
        'laps': laps,
        'request': context['request'],
    }

@register.inclusion_tag('records/tags/lap_results.html', takes_context=True)
def get_search(context):
    request = context['request']
    search_query = str(request.GET.get('query', None))
    best = str(request.GET.get('best', None))
    if best == 'None':
        is_best = False
    else:
        is_best = True
    
    if search_query:
        s = get_search_backend()
        laps = s.search(search_query, Lap.objects.order_by('-lap_date').filter(best=is_best), operator="and", order_by_relevance=False)
        print(laps)
    else:
        laps = Lap.objects.all().order_by('-lap_date').filter(best=is_best)

    return {
        'laps': laps,
        'request': context['request'],
    }