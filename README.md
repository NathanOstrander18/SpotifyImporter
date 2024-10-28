# SpotifyImporter
Imports mp3 files into spotify

Around 2014 I got a new laptop, switched over to spotify and completely forgot about all of the music I collected over the years. As my spotify library grew I noticed it was missing some needed nostalgia. I tried importing all of my old music into spotify but all of the song names were grayed out. Was having trouble resolving this within the App so I thought it would be a good chance to mess around with their API.

The script iterates though a given path, grabs a track's title and artist, and queries the spotify library for each track. If a track is found it is added to a new playlist called "mp3 Import". If a song isn't found then some clean up is performed on the track's title and artist in an effort to broaden the search. e.g. removing features from a song title.

