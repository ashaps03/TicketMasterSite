import base64
from requests import post, get
import json

client_id = "49c3572666b143b4be76ed181d3c8c86"
client_secret = "2ccbaef6e4b149ee947ac166ec63c430"


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist found")
        return None
    return json_result[0]


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    track_list = []
    for t in json_result:
        track = {}
        track.update({"name": t["name"]})
        track.update({"album": t['album']['name']})
        track.update({"image": t['album']['images'][0]['url']})
        track.update({"url": t['external_urls']['spotify']})
        track.update({"preview": t['preview_url']})
        track_list.append(track)
    return track_list


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


def retrieve_artist_data(data):
    artists = []
    event_list = data['event_list']
    for event in event_list:
        artists.append(event['name'])
    token = get_token()
    artists_data = []
    for artist in artists:
        info = {}
        try:
            res = search_for_artist(token, artist)
            artist_id = res["id"]
            info.update({"name": res['name']})
            info.update({"id": artist_id})
            info.update({"genre": res['genres'][0]})
            info.update({"url": res['external_urls']['spotify']})
            info.update({'image': res['images'][0]['url']})
            res = get_songs_by_artist(token, artist_id)
            info.update({"top tracks": res})
            res = get_related_to_artist(token, artist_id)
            info.update({"similar artists": res})
        except IndexError:
            continue
        except TypeError:
            continue
        artists_data.append(info)
    return artists_data
    #print(artists_data)

