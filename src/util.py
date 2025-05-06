import dbus
import requests
import json
import dbus.mainloop.glib

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

player = bus.get_object("org.mpris.MediaPlayer2.sayonara",
                        "/org/mpris/MediaPlayer2")
properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")


def get_cover_lastfm(track: str, artist: str):
    api_key = "698a7b7f60d194998373d6d52f0d57ab"
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={track}&format=json"
    headers = {'content-type': 'application/json'}
    response = requests.get(url, headers=headers)
    response_data = json.loads(response.text)

    cover_url = response_data["track"]["album"]["image"][3]["#text"]
    return cover_url


def get_metadata():
    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    song_title = metadata.get("xesam:title", "Unknown Title")
    song_artist = metadata.get("xesam:albumArtist", "Unknown Artist")
    song_length = round(metadata.get("mpris:length") / 1000000)

    return song_title, song_artist, song_length


def get_position():
    position = properties.Get("org.mpris.MediaPlayer2.Player", "Position")

    return round(position / 1000000)
