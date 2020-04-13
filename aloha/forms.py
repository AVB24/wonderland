from django import forms
from ls.joyous.models import (SimpleEventPage, MultidayEventPage, RecurringEventPage,
                              MultidayRecurringEventPage)

class MultidayEventForm(forms.ModelForm):
    class Meta:
        model = MultidayEventPage
        exclude = ['tz']
