from __future__ import absolute_import, unicode_literals
import csv
import os
import sys
import unicodedata
import re
from datetime import datetime, timedelta
from time import sleep
from django import forms
from django.db import models
from wagtail.documents.models import Document, AbstractDocument
from wagtail.core.models import Page, Orderable

from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock

from wagtail.admin.edit_handlers import (FieldPanel, InlinePanel, PageChooserPanel, MultiFieldPanel)

from wagtail.contrib.settings.models import BaseSetting, register_setting
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from records.models import Region, Event, Group, Track, Lap, RaceClass, Sponsor, Racer, Car
from django.db.models.signals import post_save
from django.dispatch import receiver
from wagtail.search.backends import get_search_backend
# The LinkFields and RelatedLink meta-models are taken from the WagtailDemo implementation.
# They provide a multi-field panel that allows you to set a link title and choose either
# an internal or external link. It also provides a custom property ('link') to simplify
# using it in the template.

class LinkFields(models.Model):
  link_external = models.URLField("External link", blank=True)
  link_page = models.ForeignKey(
    'wagtailcore.Page',
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='+'
  )

  @property
  def link(self):
    if self.link_page:
      return self.link_page.url
    else:
      return self.link_external

  panels = [
    FieldPanel('link_external'),
    PageChooserPanel('link_page'),
  ]

  class Meta:
    abstract = True

class RelatedLink(LinkFields):
  title = models.CharField(max_length=255, help_text="Link title")

  panels = [
    FieldPanel('title'),
    MultiFieldPanel(LinkFields.panels, "Link"),
  ]

  class Meta:
    abstract = True

# The SocialMediaSettings model provides site-specific social media links.
# These could be easily expanded to include any number of social media URLs / IDs.

@register_setting
class SocialMediaSettings(BaseSetting):
  facebook = models.URLField(
    help_text='Your Facebook page URL',
    null=True,
    blank=True
  )
  twitter = models.CharField(
    max_length=255,
    help_text='Your Twitter username, without the @',
    null=True,
    blank=True
  )

# The FooterLinks model takes advantage of the RelatedLink model we implemented above.

@register_setting
class FooterLinks(BaseSetting, ClusterableModel):

  panels = [
    InlinePanel('footer_links', label="Footer Links"),
  ]

class FooterLinksRelatedLink(Orderable, RelatedLink):
  page = ParentalKey('FooterLinks', related_name='footer_links')

# RE the SiteBranding model, you'll note that there's no custom-validation on the
# banner_colour field to check that a valid hex value has been entered. This would
# probably be better off as a select field with a set of predefined colour choices.

@register_setting
class SiteBranding(BaseSetting):
  site_logo = models.ForeignKey(
    'wagtailimages.Image',
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='+',
  )
  banner_colour = models.CharField(
    max_length=6,
    null=True,
    blank=True,
    help_text="Fill in a hex colour value"
  )

  panels = [
    ImageChooserPanel('site_logo'),
    FieldPanel('banner_colour'),
  ]

@register_setting
class PaginationSettings(BaseSetting):
  items_per_page = models.IntegerField(
    default=10
    )
  page_range = models.IntegerField(
    default=5
  )
  panels = [
    FieldPanel('items_per_page'),
    FieldPanel('page_range'),

  ]

class CustomDocument(AbstractDocument):
  # Custom field example:
  region = models.ForeignKey(Region,null=True,blank=True, on_delete=models.CASCADE)
  event = models.ForeignKey(Event,null=True,blank=True, on_delete=models.CASCADE)
  group = models.ForeignKey(Group, null=True,blank=True, on_delete=models.CASCADE)
  track = models.ForeignKey(Track, null=True,blank=True, on_delete=models.CASCADE)
  lap_date = models.DateField("Lap date", null=True,blank=True)
  

  admin_form_fields = Document.admin_form_fields + (
    # Add all custom fields names to make them appear in the form:
    'region',
    'event',
    'group',
    'track',
    'lap_date'
  )

def process_time(time):
  if time:
    if time != '0: ':
      t = datetime.strptime(time, "%M:%S.%f")
      delta = timedelta(minutes=t.minute, seconds=t.second,microseconds=t.microsecond)
      return float(delta.total_seconds())
    else:
      return 0.000
  else:
    return 0.000

def normalize_string(item):
  normStr = unicodedata.normalize('NFKD',item)
  if normStr:
    return normStr
  else:
    return "None"

def validLap(racer_class, point_in_class):
  valid = True
  if racer_class == 'None' or racer_class == 'No Class':
    print("Lap had no class")
    valid = False
  elif point_in_class == 'DQ' or point_in_class == 'DNS':
    print("Lap is DQ or DNS")
    valid = False
  return valid

@receiver(post_save, sender=CustomDocument)
def create_lap(sender, instance, created, **kwargs):
  if created == False:
    print("Create Laps")
    file = str(instance.file)
    region = instance.region
    event = instance.event
    group = instance.group
    track = instance.track
    lapsToUpload = []
    bestlaps = {}
    search_results = Lap.objects.all().filter(track=track)
    for bl in search_results:
      if bl.best is True:
        bestlaps[bl.raceclass.name] = bl

    print(file)
    if file.endswith('.csv'):
      with open('media/'+file, 'rt', encoding='ISO-8859-1') as f:
        reader = csv.DictReader(f)
        for row in reader:
        #row = row.replace('"','').replace(', ', ' ').strip()
          if 'Best Tm' in row:
            time = row['Best Tm']
          else:
            time = row['Overall BestTm']
          
          if 'Laps' in row:
            laps = row['Laps']
          else:
            laps = row['Appeared']

          position = row['Pos']
          point_in_class = row['PIC']
          carnum = row['No.']
          racer_name = normalize_string(row['Name'])
          racer_class = normalize_string(row['Class'])
          diff = row['Diff']
          gap = row['Gap']
          points = row['Points']
          car_make = normalize_string(row['Make'])
          car_model = normalize_string(row['Model'])
          car_year = row['Year']
          car_color = row['Color']
          city = row['City']
          state = row['State']
          sponsor = normalize_string(row['Sponsor'])
          email = row['Email']

          if time.count(':') == 0 and time:
            time = '0:' + time
          
          if validLap(racer_class, point_in_class):
            
            dt = datetime.strptime(str(instance.lap_date), '%Y-%m-%d')
            pt = process_time(time)
            #t = track #Track.get_or_insert(key_name=self.request.get('track'), name=self.request.get('track'), lap_distance=1.02)
            #g = self.request.get('group')
            #sd = self.request.get('date')
            #dt = datetime.strptime(sd, '%Y-%m-%d')
            #tr = Track.get_or_insert(key_name=t, name=t)
            #e = Event.get_or_insert(key_name=g+t+sd, name=g+t, track=tr, date=dt)
            if pt != 0.000:
              c, c_created = Car.objects.get_or_create(make=car_make, model=car_model,year=car_year,color=car_color,number=carnum)
              print('New Car: ' + str(c_created))
              cl, cl_created = RaceClass.objects.get_or_create(name=racer_class)
              print('New RaceClass: ' + str(cl_created))
              print(email)
              print(racer_name)
              if email is None or email == '':
                email = racer_name.replace(" ", ".") + '@gmail.com'
                print(email)
                print(racer_name)
              r, r_created = Racer.objects.get_or_create(email=email.lower(),name=racer_name)
              print('New Racer: ' + str(r_created))
              r.points=int(points)
              r.cars.add(c)

              if sponsor:
                sponsors = re.split("\s+,\s+", sponsor)
                s1 = []
                for s in sponsors:
                  s, s_created=Sponsor.objects.get_or_create(name=sponsor)
                  print('New Sponsor: ' + str(s_created))
                  r.sponsors.add(s)
              r.save()
              lap, lap_created = Lap.objects.get_or_create(racer=r, group=group, raceclass=cl, car=c, event=event, region=region, track=track, time=pt, lap_date=dt, best=False)
              print('New Lap: ' + str(lap_created))
              if cl.name in bestlaps:
                if pt < bestlaps[cl.name].time and pt != 0.0:
                  print(str(pt) + ' is better than ' + bestlaps[cl.name].racer.name + 's time of ' + str(bestlaps[cl.name].time))
                  lap.best = True					#Mark current record as best
                  bestlaps[cl.name].best = False	#Mark old record as not best
                  bestlaps[cl.name].save()				#Commit old record to db
                  bestlaps[cl.name] = lap 			#Replace record in local dictionary with new best record for class
              elif pt != 0.0:
                lap.best = True
                bestlaps[cl.name] = lap
              lap.save()
              lapsToUpload.append(lap)
        #db.put(lapsToUpload)
        print(lapsToUpload)