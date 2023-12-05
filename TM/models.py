from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

from TM.views import EventView


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


class FormCollection(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    favorite_artist = models.CharField(max_length=255)
    favorite_genre = models.CharField(max_length=255)
    preferred_timeframe_start = models.DateField()
    preferred_timeframe_end = models.DateField()

    def __str__(self):
        return f"{self.user.username}'s Form Collection"



class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(EventView, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} likes {self.event.name}'

