from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.core.models import Page
from wagtail.search.models import Query
from records.models import Lap
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

def search(request):
    search_query = request.GET.get('query', None)
    best = str(request.GET.get('best', None))
    page = request.GET.get('page', 1)

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
    paginator = Paginator(search_results, 1)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'records/lap_page.html', {
        'search_query': search_query,
        'search_results': search_results,
        'best': is_best,
    })