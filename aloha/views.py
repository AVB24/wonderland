from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify

from .forms import MultidayEventForm

from wagtail.admin.utils import send_notification

# Create your views here.
def submit_multidayevent(request):
    form = MultidayEventForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        multidayevent_page = form.save(commit=False)
        multidayevent_page.slug = slugify(multidayevent_page.title)
        event = calendar.add_child(instance=multidayevent_page)
        if event:
            event.unpublish()
            # Submit page for moderation. This requires first saving a revision.
            event.save_revision(submitted_for_moderation=True)
            # Then send the notification to all Wagtail moderators.
            send_notification(event.get_latest_revision().id, 'submitted', None)
        return HttpResponseRedirect(calendar.url + calendar.reverse_subpage('thanks'))
    context = {
        'form': form,
    }
    return render(request, 'multidayevent_page_add.html', context)