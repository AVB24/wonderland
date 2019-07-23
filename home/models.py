from django.db import models

from wagtail.core.models import Page
from wagtailmetadata.models import MetadataPageMixin
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel


class HomePage(MetadataPageMixin, Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]
    def get_context(self, request, *args, **kwargs):
        context = super(HomePage, self).get_context(request, *args, **kwargs)

        context['menuitems'] = self.get_children().filter(
            live=True, show_in_menus=True)

        return context