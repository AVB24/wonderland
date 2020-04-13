from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from ls.joyous.models import (SimpleEventPage, MultidayEventPage, RecurringEventPage,
                              MultidayRecurringEventPage, removeContentPanels)

# Hide unwanted event types
RecurringEventPage.is_creatable = False
MultidayRecurringEventPage.is_creatable = False

# Hide unwanted content
removeContentPanels(["category", "tz", "group_page", "website"])

# Create your models here.
