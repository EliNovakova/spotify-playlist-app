from bs4 import BeautifulSoup
import requests
import spotipy
import pprint
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "<INSERT-CLIENT-ID>"    # specific for each Spotify user account
CLIENT_SECRET = "<INSERT-CLIENT-SECRET"     # specific for each Spotify user account


# Accessing top songs with BeautifulSoup
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:")
year = date.split("-")[0]   # to get the year from the date


response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")

webpage = response.text

soup = BeautifulSoup(webpage, "html.parser")
all_songs = soup.find_all(name="span", class_="chart-element__information__song")
song_list = []
for song in all_songs:
    song_name = song.getText()
    song_list.append(song_name)

print(song_list)

# Spotify authorization
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri="http://example.com",  # example site that opens when we run authentication (we need to copy its url then)
        scope="playlist-modify-private",    # this is from the documentation
    )
)

user_id = sp.current_user()["id"]   # gets current users id


# search Spotify for songs from song_list
uri_list = []   # we need to obtain Spotify uri (unique identifier) for each song from our list
for song in song_list:
    song_info = sp.search(q=f"track: {song} year: {year}", type="track", limit=1)   # search by track name and release year
    # pprint.pprint(song_info)
    try:    # if song under that name is found on Spotify
        song_uri = song_info["tracks"]["items"][0]["uri"]   # we get it's uri
        # pprint.pprint(song_uri)
        uri_list.append(song_uri)   # and add this uri to the uri list
    except IndexError:  # if it's not on Spotify, we catch this error
        print(f"{song} is not on Spotify.")

print(uri_list)

# Creating Spotify playlist
playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{date} Billboard 100",   # name of the playlist
    public=False,   # not public!! based on the scope we use
)

playlist_id = playlist["id"]    # gets playlist id to use it later when adding songs

pprint.pprint(playlist)
print(playlist_id)

# Adding songs to the playlist
sp.playlist_add_items(
    playlist_id=playlist_id,
    items=uri_list,
)
