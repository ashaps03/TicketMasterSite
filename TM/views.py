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
from TM.models import Event, FormCollection, Favorite


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

def parse_and_save_data(data, user):
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
            image = event["images"][0]["url"]
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

            # Save the event to the database
            event_model = Event(
                user=user,
                name=name,
                image=image,
                date=date_str,
                time=time_str,
                venue=venue_name,
                city=city,
                state=state,
                address=address,
                url=url
            )
            event_model.save()

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
            image = event["images"][0]["url"]
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


# Create your views here.
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
            return render(request, 'results.html', context=data)
    return render(request, 'results.html')


def home_page(request):
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
            return render(request, 'results.html', context=data)

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

def logout_view(request):
    logout(request)
    messages.info(request, "Successfully logged out.")
    return redirect('ticketmaster_view')


def likes(request):
    return None

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


class LikedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(EventView, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} likes {self.event.name}'

    def likes(request):
        # Assuming you want to retrieve liked events for the currently logged-in user
        user = request.user

        if user.is_authenticated:
            liked_events = EventView.objects.filter(likes=user)
            context = {'liked_events': liked_events}
            return render(request, 'likes.html', context)
        else:
            return redirect('login')

def form_page(request):
    return render(request, 'form_page.html')



@login_required
def submit_profile(request):
    if request.method == 'POST':
        favorite_artist = request.POST.get('favorite_artist')
        favorite_genre = request.POST.get('favorite_genre')
        preferred_timeframe_start = request.POST.get('preferred_timeframe_start')
        preferred_timeframe_end = request.POST.get('preferred_timeframe_end')
        location = request.POST.get('location')  # Retrieve location separately



        form_collection = FormCollection(
            user=request.user,
            favorite_artist=favorite_artist,
            favorite_genre=favorite_genre,
            preferred_timeframe_start=preferred_timeframe_start,
            preferred_timeframe_end=preferred_timeframe_end,
        )
        form_collection.save()

        return redirect('form_results')

    return render(request, 'form_results')

def form_results(request):
    if request.method == 'POST':
        # Retrieve form data
        favorite_artist = request.POST.get('favorite_artist', '')
        favorite_genre = request.POST.get('favorite_genre', '')
        preferred_timeframe_start = request.POST.get('preferred_timeframe_start', '')
        preferred_timeframe_end = request.POST.get('preferred_timeframe_end', '')
        location = request.POST.get('location', '')  # Retrieve location from form data


        # Get events from the Ticketmaster API
        data = get_events(favorite_artist, location)

        # Check if events are found
        if data and data.get('_embedded', {}).get('events', []):
            # Parse and save data to the database
            user = request.user if request.user.is_authenticated else None
            parse_and_save_data(data, user)

            # Parse data for display
            context = parse_data(data)

            return render(request, 'form_results.html', context)
        else:
            messages.error(request, 'No events found for your preferences.')

    # If the request method is not POST or no events found, redirect to the form page
    return redirect('form_page')

def like_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        user = request.user

        # Check if the user already liked this event
        if not Favorite.objects.filter(user=user, event_id=event_id).exists():
            # Create a new Favorite entry
            Favorite.objects.create(user=user, event_id=event_id)
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})