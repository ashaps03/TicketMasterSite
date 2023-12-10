# Remove the import of EventView from TM.views
# from TM.views import EventView
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.URLField()
    date = models.CharField(max_length=20)
    time = models.CharField(max_length=20)
    venue = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return self.name



class LikedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=255, default='Unknown Event')
    event_image = models.URLField(default='default_image_url')
    event_date = models.CharField(max_length=20, default=timezone.now)
    event_time = models.CharField(max_length=20, default=timezone.now)
    event_venue = models.CharField(max_length=255, default='Unknown')
    event_city = models.CharField(max_length=255, default='Unknown')
    event_state = models.CharField(max_length=255, default='Unknown')
    event_address = models.CharField(max_length=255, default='')  # Set the default value
    event_url = models.URLField(default='')

    def __str__(self):
        return self.event_name
@method_decorator(login_required, name='dispatch')
class LikedEventListView(View):
    template_name = 'liked_events.html'

    def get(self, request, *args, **kwargs):
        liked_events = LikedEvent.objects.filter(user=request.user)
        context = {'liked_events': liked_events}
        return render(request, self.template_name, context)
