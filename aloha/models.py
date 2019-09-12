from django.db import models
from ls.joyous.models import (SimpleEventPage, MultidayEventPage, RecurringEventPage,
                              MultidayRecurringEventPage, removeContentPanels)

# Hide unwanted event types
RecurringEventPage.is_creatable = False
MultidayRecurringEventPage.is_creatable = False

# Hide unwanted content
removeContentPanels(["category", "tz", "group_page", "website"])

# Create your models here.
