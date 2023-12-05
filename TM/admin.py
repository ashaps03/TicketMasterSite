from django.contrib import admin

from TM.models import FormCollection
from TM.views import EventView


# Register your models here.

@admin.register(EventView)
class EventAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'date', 'time', 'venue', 'city', 'state', 'address', 'url')
    search_fields = ('name', 'venue', 'city', 'state', 'address')  # Optional: Add search functionality

@admin.register(FormCollection)
class FormCollectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'favorite_artist', 'favorite_genre', 'preferred_timeframe_start', 'preferred_timeframe_end']
    search_fields = ['user__username', 'favorite_artist', 'favorite_genre']