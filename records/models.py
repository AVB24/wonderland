from django import forms
from django.db import models
from django.contrib.auth.models import User
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField

from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.edit_handlers import (FieldPanel)
from wagtail.snippets.models import register_snippet
from wagtail.search import index
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class MemberPage(Page):
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
    ]

@register_snippet
class Track(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('short_name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'tracks'

@register_snippet
class Event(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    tracks = models.ManyToManyField(Track)
    external_id = models.IntegerField()

    panels = [
        FieldPanel('name'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
        FieldPanel('tracks', widget=forms.SelectMultiple),
        FieldPanel('external_id'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'events'

@register_snippet
class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'sponsors'

@register_snippet
class RaceClass(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
        FieldPanel('short_name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'raceclasses'

@register_snippet
class Car(models.Model):
    make = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    year = models.CharField(max_length=4)
    color = models.CharField(max_length=255)
    number = models.CharField(max_length=10)

    panels = [
        FieldPanel('make'),
        FieldPanel('model'),
        FieldPanel('year'),
        FieldPanel('color'),
        FieldPanel('number'),
    ]

    def __str__(self):
        return "#%s:%s_%s" % (self.number, self.make, self.model)

    class Meta:
        verbose_name_plural = 'cars'

@register_snippet
class Racer(models.Model):
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    name = models.CharField(max_length=255)
    bio = models.CharField(max_length=255,null=True,blank=True)
    birth_date = models.DateField(null=True,blank=True)
    city = models.CharField(max_length=255,null=True,blank=True)
    state = models.CharField(max_length=255,null=True,blank=True)
    points = models.IntegerField(null=True,blank=True)
    cars = models.ManyToManyField(Car)
    sponsors = models.ManyToManyField(Sponsor,blank=True)

    panels = [
        ImageChooserPanel('icon'),
        FieldPanel('user', widget=forms.Select),
        FieldPanel('email', widget=forms.EmailInput),
        FieldPanel('name'),
        FieldPanel('bio'),
        FieldPanel('birth_date'),
        FieldPanel('city'),
        FieldPanel('state'),
        FieldPanel('points'),
        FieldPanel('cars', widget=forms.SelectMultiple),
        FieldPanel('sponsors', widget=forms.SelectMultiple),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'racers'

@register_snippet
class Group(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
        FieldPanel('short_name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'groups'

@register_snippet
class Region(models.Model):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255,null=True,blank=True)
    short_name = models.CharField(max_length=255)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('link'),
        FieldPanel('short_name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'regions'

@register_snippet
class Lap(index.Indexed, models.Model):
    racer = models.ForeignKey(Racer, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    raceclass = models.ForeignKey(RaceClass, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, blank=True,on_delete=models.CASCADE)
    event = models.ForeignKey(Event,null=True,blank=True, on_delete=models.CASCADE)
    region = models.ForeignKey(Region,null=True,blank=True, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    time = models.FloatField()
    lap_date = models.DateField("Lap date")
    best = models.BooleanField("Is Best?")

    search_fields = [
        index.FilterField('best'),
        index.FilterField('lap_date'),

        index.RelatedFields('racer', [
            index.SearchField('name', partial_match=True),
        ]),
        index.RelatedFields('raceclass', [
            index.SearchField('name', partial_match=True),
        ]),
        index.RelatedFields('track', [
            index.SearchField('name', partial_match=True),
        ]),
    ]

    panels = [
        FieldPanel('region', widget=forms.Select),
        FieldPanel('racer', widget=forms.Select),
        FieldPanel('raceclass', widget=forms.Select),
        FieldPanel('car', widget=forms.Select),
        FieldPanel('group', widget=forms.Select),
        FieldPanel('event', widget=forms.Select),
        FieldPanel('track', widget=forms.Select),
        FieldPanel('time'),
        FieldPanel('lap_date'),
        FieldPanel('best'),
    ]

    def __str__(self):
        return "racer='%s', raceclass='%s', car='%s', event='%s', time='%s'" % (self.racer, self.raceclass, self.car, self.event, self.time)

    class Meta:
        verbose_name_plural = 'laps'
        constraints = [
            models.UniqueConstraint(fields=['racer', 'group', 'raceclass', 'track', 'lap_date'], name='key'),
        ]

@receiver(post_save, sender=User)
def create_user_racer(sender, instance, created, **kwargs):
    if created:
        Racer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_racer(sender, instance, **kwargs):
    instance.racer.save()