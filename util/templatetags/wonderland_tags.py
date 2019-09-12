from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import math, datetime
from django import template
from django.conf import settings

from wagtail.core.models import Page
from wagtail.search.models import Query

from django.contrib.auth.models import User
from records.models import Lap,Event
from util.models import PaginationSettings
from wagtail.search.backends import get_search_backend
from datetime import datetime

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
    return context['request'].site.site_name


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


@register.simple_tag(takes_context=True)
def get_member_laps(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    request = context['request']
    search_query = request.GET.get('query', '')
    best = str(request.GET.get('best', None))
    page = request.GET.get('page', 1)
    pagination_settings = PaginationSettings.for_site(request.site)
    path_info = request.META['PATH_INFO']
    user = User.objects.filter(username=request.user).first()

    if hasattr(user, 'racer'):
        racer_name = user.racer.name
    else:
        racer_name = ''

    if best == 'None':
        is_best = False
    else:
        is_best = True
    search_query = racer_name + ' ' + search_query
    if search_query:
        s = get_search_backend()
        if is_best:
            search_results = s.search(search_query, Lap.objects.order_by('-lap_date').filter(best=is_best), operator="and", order_by_relevance=False)
        else:
            search_results = s.search(search_query, Lap.objects.order_by('-lap_date'), operator="and", order_by_relevance=False)
        #search_results = Page.objects.live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        #search_results = Page.objects.none()
        if is_best:
            search_results = Lap.objects.all().order_by('-lap_date').filter(best=is_best)
        else:
            search_results = Lap.objects.all().order_by('-lap_date')

    # Pagination
    paginator = Paginator(search_results, pagination_settings.items_per_page)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    if is_best == False:
        is_best = 'None'

    return search_results

@register.simple_tag(takes_context=True)
def get_next_events(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    request = context['request']
    site = str(request.site)
    today = datetime.now().date()
    path = request.path_info
    if 'Lap Records' in site and path == '/':
        print("GOTEE")
        event_results = Event.objects.filter(external_id__isnull=False).filter(start_date__gte=today)
    else:
        event_results = ""
    return event_results