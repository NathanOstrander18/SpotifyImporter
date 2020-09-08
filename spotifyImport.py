import eyed3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser
import os
import pandas as pd

eyed3.log.setLevel("ERROR")

config = configparser.ConfigParser()                                     
config.read('config.ini')

client_id = config.get('SPOTIFY', 'CLIENT_ID')
client_secret_id = config.get('SPOTIFY', 'CLIENT_SECRET_ID')
user_id = config.get('SPOTIFY', 'USER_ID')
redirect_uri = config.get('SPOTIFY', 'REDIRECT_URI')
path = config.get('DIRECTORY', 'PATH')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,client_secret=client_secret_id, redirect_uri=redirect_uri, scope='playlist-modify-private playlist-modify-public', show_dialog=True, cache_path=".cache-" + "test"))

expletives = ["shit", "fuck"]
counter = 0
track_ids = []
df = pd.DataFrame(columns=['Track Tag', 'Artist Tag', 'Query 1', 'Query 2', 'Track', 'Artist', 'Track ID', 'Total Results'])

playlist = sp.user_playlist_create(user_id, "mp3 Import", public=True, collaborative=False, description='')

for subdir, dirs, files in os.walk(path):
    for file in files:
        try:
            if file.endswith(".mp3"):
                entryDict = {'File Name': file, 'Track Tag': '', 'Artist Tag': '', 'Query 1': '', 'Query 2': '', 'Track': '', 'Artist': '', 'Track ID': '', 'Total Results': 0, 'Exception': ''}
                filePath = os.path.join(subdir, file)
                audio = None
                try:
                    audio = eyed3.load(filePath)
                except Exception as e:
                    print("An exception occurred loading mp3")
                    print(file)
                    print(e)
                    entryDict['Exception'] = e
                if audio is not None:
                    title = audio.tag.title
                    artist = audio.tag.artist
                    entryDict['Track Tag'] = title
                    entryDict['Artist Tag'] = artist
                    if title:
                        title = title.lower()
                        artist = artist.lower() if artist else ""
                        if "(feat" in title or "(bonus" in title:
                            title = title.split("(")[0]
                        q = "artist:"+ (artist) +" track:"+title
                        entryDict['Query 1'] = q
                        results = None
                        try:
                            results = sp.search(q=q, type="track", limit=1)
                        except Exception as e:
                            print("An exception occurred during song query")
                            print(q)
                            entryDict['Exception'] = e
                        if results is not None:
                            if results.get("tracks").get("total") == 0:
                                for curse in expletives:
                                    title = title.replace(curse, "")
                                if "(" in title:
                                    title = title.split("(")[0]
                                if "feat" in title:
                                    title = title.split("feat")[0]
                                if "ft." in title:
                                    title = title.split("ft.")[0]
                                if "&" in artist:
                                    artist = title.split("&")[0]
                                q = "artist:"+ (artist) +" track:"+title
                                entryDict['Query 2'] = q
                                try:
                                    results = sp.search(q=q, type="track", limit=1)
                                except Exception as e:
                                    print("An exception occurred during song query")
                                    print(q)
                                    entryDict['Exception'] = e
                            if results is not None:
                                entryDict['Total Results'] = results.get("tracks").get("total")
                                if results.get("tracks").get("total") > 0:
                                    item = results.get('tracks').get('items')[0]
                                    entryDict['Track'] = item.get("name")
                                    entryDict['Artist'] = item.get("artists")[0].get("name")
                                    entryDict['Track ID'] = item.get("id")
                                    print(str(counter) + ": " + item.get("name"))
                                    track_ids.append(item.get("id"))
                                    counter = counter + 1
                                    if counter == 100:
                                        sp.playlist_add_items(playlist.get("id"), track_ids, position=None)
                                        print("added to playlist")
                                        counter = 0
                                        track_ids = []
                        df = df.append(entryDict, ignore_index=True)
        except Exception as e:
            print("An exception occurred")
            print(e)
    if track_ids:
        sp.playlist_add_items(playlist.get("id"), track_ids, position=None)
    

df.to_csv("spotify_import_report.csv", index=False)

