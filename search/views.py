from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.search.models import Query
from records.models import Lap
from util.models import PaginationSettings
from wagtail.search.backends import get_search_backend


def search(request):
    search_query = request.GET.get('query', None)
    best = str(request.GET.get('best', None))
    page = request.GET.get('page', 1)
    pagination_settings = PaginationSettings.for_site(request.site)

    if best == 'None':
        is_best = False
    else:
        is_best = True
    # Search
    if search_query:
        s = get_search_backend()
        search_results = s.search(search_query, Lap.objects.order_by('-lap_date').filter(best=is_best), operator="and", order_by_relevance=False)
        #search_results = Page.objects.live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        #search_results = Page.objects.none()
        search_results = Lap.objects.all().order_by('-lap_date').filter(best=is_best)

    # Pagination
    paginator = Paginator(search_results, pagination_settings.items_per_page)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
        'best': is_best,
    })
