from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.search.models import Query
from records.models import Lap
from util.models import PaginationSettings
from wagtail.search.backends import get_search_backend


def search(request):
    search_query = request.GET.get('query', '')
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

     # Get the index of the current page
    index = search_results.number - 1  # edited to something easier without index
    # This value is maximum index of your pages, so the last page - 1
    max_index = len(paginator.page_range)
    # You want a range of 7, so lets calculate where to slice the list
    start_index = index - pagination_settings.page_range if index >= pagination_settings.page_range else 0
    end_index = index + pagination_settings.page_range if index <= max_index - pagination_settings.page_range else max_index
    # Get our new page range. In the latest versions of Django page_range returns 
    # an iterator. Thus pass it to list, to make our slice possible again.
    page_range = list(paginator.page_range)[start_index:end_index]

    if is_best == False:
        is_best = 'None'

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
        'best': is_best,
        'page_range': page_range,
    })
