from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
from datetime import datetime
import pytz
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import models
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from TM.models import Event, LikedEvent
from spotify import spotifyAPI
from spotify.spotifyAPI import retrieve_artist_data


def get_events(searchTerm, location):
    try:
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        apikey = "9fuArG8p0y2IDcEnEI2znyOX4GkbGgWM"
        parameters = {
            "classificationName": searchTerm,
            "city": location,
            "sort": 'date,asc',
            "apikey": apikey
        }
        response = requests.get(url, params=parameters)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def get_highest_resolution_image(images):
    if images:
        # Sort images by width in descending order
        sorted_images = sorted(images, key=lambda x: x["width"], reverse=True)
        return sorted_images[0]["url"]
    else:
        return None


def parse_data(data):
    return_data = {
        "success": True,
        "events": 0,
        "event_list": []
    }
    try:
        embedded = data["_embedded"]
    except:
        print("nothing found")
        return return_data
    else:
        events = embedded["events"]
        for event in events:
            name = event["name"]

            # Choose the image with the highest resolution
            image = get_highest_resolution_image(event.get("images", []))

            datetime_str = event["dates"]["start"].get("dateTime")
            datetime_format = "%Y-%m-%dT%H:%M:%SZ"
            try:
                datetime_obj = (datetime.strptime(datetime_str, datetime_format).replace(tzinfo=pytz.timezone("UTC"))
                                .astimezone(pytz.timezone("US/Eastern")))
                date_str = datetime_obj.date().strftime('%a %b %d %Y')
                time_str = datetime_obj.time().strftime('%I:%M %p')
            except:
                date_str = "Date Unavailable"
                time_str = "Time Unavailable"
            venue = event["_embedded"]["venues"][0]
            venue_name = venue["name"]
            city = venue["city"]["name"]
            state = venue["state"]["name"]
            address = venue["address"]["line1"]
            url = event["url"]

            event_details = {
                'name': name,
                'image': image,
                'date': date_str,
                'time': time_str,
                'venue': venue_name,
                'city': city,
                'state': state,
                'address': address,
                'url': url
            }
            return_data["event_list"].append(event_details)
        return_data["events"] = len(events)
        return return_data


@login_required(redirect_field_name=None)
def tm_view(request):
    if request.method == "POST":
        search_term = request.POST['searchTerm']
        location = request.POST['location']
        if not search_term:
            messages.info(request, "Search term cannot be empty. Please enter a search term.")
            return redirect('ticketmaster_view')
        if not location:
            messages.info(request, "City cannot be empty. Please enter a city.")
            return redirect('ticketmaster_view')
        data = get_events(search_term, location)
        if data is None:
            messages.info(request, 'The server encountered an issue while fetching data. Please try again later.')
            return redirect('ticketmaster_view')
        else:
            data = parse_data(data)
            # events = data['event_list']
            # artists = spotifyAPI.retrieve_artist_data(data)
            # print(artists)
            # events_artists = zip(events, artists)
            # data.update({'event_list': events_artists})
            return render(request, 'results.html', context=data)
    return render(request, 'results.html')


def home_page(request):
    # if request.method == "POST":
    #     search_term = request.POST['searchTerm']
    #     location = request.POST['location']
    #     if not search_term:
    #         messages.info(request, "Search term cannot be empty. Please enter a search term.")
    #         return redirect('ticketmaster_view')
    #     if not location:
    #         messages.info(request, "City cannot be empty. Please enter a city.")
    #         return redirect('ticketmaster_view')
    #     data = get_events(search_term, location)
    #     if data is None:
    #         messages.info(request, 'The server encountered an issue while fetching data. Please try again later.')
    #         return redirect('ticketmaster_view')
    #     else:
    #         data = parse_data(data)
    #         spotifyAPI.retrieve_artist_data(data)
    #         return render(request, 'results.html', context=data)

    return render(request, 'home.html')


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required( redirect_field_name=None)
def logout_view(request):
    logout(request)
    messages.info(request, "Successfully logged out.")
    return redirect('ticketmaster_view')


@login_required(redirect_field_name=None)
def likes(request):
    return None


@login_required(redirect_field_name=None)
class EventView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.URLField()
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    url = models.URLField()
    likes = models.ManyToManyField(User, related_name='liked_events', blank=True)

    def __str__(self):
        return self.name


@login_required( redirect_field_name=None)
@require_POST
def like_event(request):
    if request.method == 'POST':
        event_name_with_date = request.POST.get('name', 'Unknown Event')

        event_name = event_name_with_date.rsplit(' ', 3)[0]

        event_venue = request.POST.get('venue', 'Unknown')
        event_city = request.POST.get('cityState', 'Unknown')

        is_liked = LikedEvent.objects.filter(
            user=request.user,
            event_name=event_name,
            event_venue=event_venue,
            event_city=event_city,
        ).exists()

        if is_liked:
            return JsonResponse({'success': False, 'message': 'Event already liked!'})

        liked_event = LikedEvent(
            user=request.user,
            event_name=event_name,
            event_venue=event_venue,
            event_city=event_city,
        )

        liked_event.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(redirect_field_name=None)
def remove_from_liked(request, event_id):
    if request.method == 'DELETE':
        try:
            liked_event = LikedEvent.objects.get(id=event_id)
            liked_event.delete()
            return JsonResponse({'success': True})
        except LikedEvent.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required( redirect_field_name=None)
def audio(request, data=None):
    if data is None:
        data = {}

    retrieve_artist_data(data)

    return render(request, 'audio.html', {'data': data})
