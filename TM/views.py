from django.shortcuts import render, redirect
import requests
from datetime import datetime
import pytz
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from spotify import spotifyAPI


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
            spotify_data = spotifyAPI.retrieve_artist_data(data)
            event_list = data['event_list']
            events_artists = zip(event_list, spotify_data)
            data.update({"event_list": events_artists})
            return render(request, 'results.html', data)
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
            spotify_data = spotifyAPI.retrieve_artist_data(data)
            event_list = data['event_list']
            events_artists = zip(event_list, spotify_data)
            data.update({"event_list": events_artists})
            return render(request, 'results.html', data)
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