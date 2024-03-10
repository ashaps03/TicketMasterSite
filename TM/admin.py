from django.contrib import admin

from TM.models import LikedEvent
from TM.views import EventView


# Register your models here.

@admin.register(EventView)
class EventAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'date', 'time', 'venue', 'city', 'state', 'address', 'url')
    search_fields = ('name', 'venue', 'city', 'state', 'address')  # Optional: Add search functionality

@admin.register(LikedEvent)
class LikedEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_name', 'event_venue', 'event_city', 'event_state', 'event_address', 'event_url')

    search_fields = ('event_name', 'event_venue', 'event_city', 'event_state')

