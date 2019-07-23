from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.core.models import Page
from wagtail.search.models import Query

from django.contrib.auth.models import User
from records.models import Lap
from util.models import PaginationSettings
from wagtail.search.backends import get_search_backend

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'includes/signup.html', {'form': form})

def member(request):
    search_query = request.GET.get('query', '')
    best = str(request.GET.get('best', None))
    page = request.GET.get('page', 1)
    pagination_settings = PaginationSettings.for_site(request.site)
    path_info = request.META['PATH_INFO']
    user = User.objects.filter(username=request.user).first()
    print(path_info)
    
    if hasattr(user, 'racer'):
        racer_name = user.racer.name
    else:
        racer_name = ''
        
    search_query = racer_name + ' ' + search_query

    if best == 'None':
        is_best = False
    else:
        is_best = True
    print(search_query)
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

    if is_best == False:
        is_best = 'None'

    return render(request, 'records/member_page.html', {
        'search_query': search_query,
        'search_results': search_results,
        'best': is_best,
    })