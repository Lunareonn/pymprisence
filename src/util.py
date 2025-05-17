import dbus
import base64
import dbus.mainloop.glib
import urllib.parse
from diskcache import Cache
import json
import tomllib
from configuration import config_folder
import xxhash
import os
import aiohttp

cache = Cache("./cache")

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

player = bus.get_object("org.mpris.MediaPlayer2.sayonara",
                        "/org/mpris/MediaPlayer2")
properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")


async def get_players() -> list:
    names = bus.list_names()
    if names is None:
        return []

    players = [service for service in names if service.startswith("org.mpris.MediaPlayer2.")]
    return players


async def check_if_ignored(player) -> bool:
    with open(os.path.join(config_folder, "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)

    normal_player = player.replace("org.mpris.MediaPlayer2.", "")

    if normal_player == "playerctld":
        return True

    try:
        if cfg_file["player"][normal_player]["ignore"] is True:
            return True
    except KeyError:
        if cfg_file["player"]["default"]["ignore"] is True:
            return True
        else:
            return False

    return False


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


async def upload_imgbb(file: str, track: str, artist: str) -> str:
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


def get_metadata() -> tuple:
    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    song_title = metadata.get("xesam:title", "Unknown Title")
    song_artist = metadata.get("xesam:artist", "Unknown Artist")[0]
    song_length = round(metadata.get("mpris:length") / 1000000)
    cover_path = urllib.parse.urlparse(metadata.get("mpris:artUrl")).path

    return song_title, song_artist, song_length, cover_path


def get_position() -> int:
    position = properties.Get("org.mpris.MediaPlayer2.Player", "Position")

    return round(position / 1000000)


def get_state() -> str:
    state = properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
    return state


def get_trackid() -> str:
    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    trackid = metadata.get("mpris:trackid")

    return trackid
