import dbus
import base64
import dbus.mainloop.glib
import urllib.parse
from diskcache import Cache
import json

import xxhash
import aiohttp

cache = Cache("./cache")

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

player = bus.get_object("org.mpris.MediaPlayer2.strawberry",
                        "/org/mpris/MediaPlayer2")
properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")


async def get_players():
    players = [service for service in bus.list_names(
    ) if service.startswith("org.mpris.MediaPlayer2.")]
    return players


async def cache_cover(file: str, url: str):
    hasher = xxhash.xxh64()
    with open(str(file), "rb") as f:
        while chunk := f.read(1048576):
            hasher.update(chunk)
        print(hasher.hexdigest())

    data_json = {
        "cover_url": url
    }
    cache.set(hasher.hexdigest(), json.dumps(data_json))


async def upload_imgbb(file: str, track: str, artist: str):
    api_key = "d62a1f991e1c733a1d39afb9854802c7"
    url = "https://api.imgbb.com/1/upload"

    async with aiohttp.ClientSession() as session:
        with open(str(file), "rb") as img:
            payload = {
                "key": api_key,
                "image": base64.b64encode(img.read()).decode(),
            }

        async with session.post(url, data=payload) as response:
            data = await response.json()
            print("image uploaded, hopefully async")
            print(data)
            await cache_cover(file, data["data"]["image"]["url"])
            return data["data"]["image"]["url"]


def get_metadata():
    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    song_title = metadata.get("xesam:title", "Unknown Title")
    song_artist = metadata.get("xesam:artist", "Unknown Artist")[0]
    song_length = round(metadata.get("mpris:length") / 1000000)
    cover_path = urllib.parse.urlparse(metadata.get("mpris:artUrl")).path

    return song_title, song_artist, song_length, cover_path


def get_position():
    position = properties.Get("org.mpris.MediaPlayer2.Player", "Position")

    return round(position / 1000000)


def get_state():
    state = properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
    return state


def get_trackid():
    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    trackid = metadata.get("mpris:trackid")

    return trackid
