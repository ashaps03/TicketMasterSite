import base64
from requests import post, get
import json

client_id = "49c3572666b143b4be76ed181d3c8c86"
client_secret = "2ccbaef6e4b149ee947ac166ec63c430"


#def get_token():
    #auth_string = client_id + ":" + client_secret
   # auth_bytes = auth_string.encode("utf-8")
   # auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

   # url = "https://accounts.spotify.com/api/token"
   # headers = {
     #   "Authorization": "Basic " + auth_base64,
      #  "Content-Type": "application/x-www-form-urlencoded"
   # }
   # data = {"grant_type": "client_credentials"}
   # result = post(url, headers=headers, data=data)
   # json_result = json.loads(result.content)
   # token = json_result["BQALP41L_Bm2Mt-ew0EEEmPMw-IqdiXpwXIVS_c8iQXv-w_tManDZGyAKA5RS5I_5_dtLetpgZ1AtR9sbfh6wceNhRYA31jKa_2uD8ZvNIdwt5KXGqUOSOuvyhmbRkO8jxqkFHrk9GoZ4TJCuw2MazE4Tqr0FyCBcDMhTZ7ZG4sNgwXBi7Mg4vEbXPxRpSQJJAaAPA7wkg
#"]
   # return token

def get_token():                            # This function is used to get the access token from Spotify API and will refresh once expired.
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    if 'access_token' in json_result:
        return json_result["access_token"]
    else:
        print("Failed to get access token")
        return None



def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    print(result.content)  # Add this line to print the entire response
    json_result = json.loads(result.content)
    if 'artists' in json_result and 'items' in json_result['artists']:
        if len(json_result["artists"]["items"]) == 0:
            print("No artist found")
            return None
        return json_result["artists"]["items"][0]
    else:
        print("Unexpected response from Spotify API")
        return None


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    print(result)
    json_result = json.loads(result.content)["tracks"]
    print(json_result)
    track_list = []
    for t in json_result:
        track = {}
        track.update({"name": t["name"]})
        track.update({"album": t['album']['name']})
        track.update({"image": t['album']['images'][0]['url']})
        track.update({"url": t['external_urls']['spotify']})
        track.update({"preview": t['preview_url']})
        track_list.append(track)
    return track_list[:10]  # Return only the first 10 songs

def get_related_to_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["artists"]
    related_list = []
    for i in range(5):
        artist = {}
        artist.update({"name": json_result[i]['name']})
        artist.update({"image": json_result[i]['images'][0]['url']})
        artist.update({"url": json_result[i]['external_urls']['spotify']})
        related_list.append(artist)
    return related_list

def get_recent_album(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    params = {"include_groups": "album", "limit": 1}
    result = get(url, headers=headers, params=params)
    json_result = json.loads(result.content)["items"]
    if json_result:
        album = json_result[0]
        release_year = album["release_date"].split("-")[0]  # Extract the year

        return {
            "name": album["name"],
            "id": album["id"],
            "images": album["images"],
            "release_year": release_year  # Add release year
        }
    else:
        return None

def get_album_songs(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    songs = [{"name": song["name"], 
              "duration": song["duration_ms"], 
              "artist": song["artists"][0]["name"]} for song in json_result]
    
    return songs
    




def retrieve_artist_data(data):
    artists_data = []

    if 'event_list' in data:
        event_list = data['event_list']
    else:
        print("Key 'event_list' not found in data")
        return artists_data

    token = get_token()

    for event in event_list:
        info = {}
        artist_name = event.get('name')
        try:
            res = search_for_artist(token, artist_name)
            if res:
                artist_id = res.get("id")
                info.update({"artist_name": res.get('name')})
                info.update({'artist_image': res.get('images')[0]['url']})

                album = get_recent_album(token, artist_id)
                if album:
                    info.update({"recent_album_name": album.get('name')})
                    info.update({"recent_album_image": album.get('images')[0]['url']})
                    info.update({"recent_album_release_year": album.get('release_year')})  # Add release year


                    songs = get_album_songs(token, album.get('id'))
                    info.update({"recent_album_songs": songs})

                    # Calculating album duration by summing up the duration of all songs
                    album_duration = sum(song["duration"] for song in songs)
                    info.update({"recent_album_duration": album_duration})

                    

                else:
                    # Get songs by the artist
                    songs = get_songs_by_artist(token, artist_id)
                    song_details = []
                    for song in songs:
                        song_info = {
                            "name": song.get('name'),
                            "album": song.get('album'),
                            "image": song.get('image'),
                            "url": song.get('url'),
                            "preview": song.get('preview')
                        }
                        song_details.append(song_info)
                    info.update({"recent_songs": song_details[:10]})

                artists_data.append(info)
            else:
                print(f"No artist found with the name {artist_name}")
        except Exception as e:
            print(f"An error occurred while retrieving data for {artist_name}: {e}")
            continue

    return artists_data