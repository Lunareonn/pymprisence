import dbus
import base64
import urllib.parse
from diskcache import Cache
import json
import tomllib
from configuration import config_folder
from dbus_connection import DBusSession
import xxhash
import os
import aiohttp
import re

cache = Cache("./cache")


def sanitize_player_name(player: str) -> str:
    print(player)
    player = player.replace("org.mpris.MediaPlayer2.", "")
    print(player)
    sanitized_player = re.sub(r"\..*$", "", player)
    print(sanitized_player)
    return sanitized_player


async def get_players() -> list:
    bus = DBusSession.get_bus()
    names = bus.list_names()
    if names is None:
        return []

    players = [service for service in names if service.startswith("org.mpris.MediaPlayer2.")]
    return players


async def get_current_player() -> str | None:
    bus = DBusSession.get_bus()
    players = await get_players()

    for player in players:
        try:
            proxy = bus.get_object(player, "/org/mpris/MediaPlayer2")
            interface = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            status = interface.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
            print(player, "status:", status)

            if check_if_ignored(player) is True or status in ["Stopped", "Paused"]:
                continue

            if status == "Playing":
                return player

        except dbus.DBusException:
            continue

    return None


def check_if_ignored(player) -> bool:
    with open(os.path.join(config_folder, "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)

    sanitized_player = sanitize_player_name(player)

    if sanitized_player == "playerctld":
        return True

    try:
        if cfg_file["player"][sanitized_player]["ignore"] is True:
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


def get_metadata(player) -> tuple:
    bus = DBusSession.get_bus()
    player = bus.get_object(player,
                            "/org/mpris/MediaPlayer2")
    properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")
    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    song_title = metadata.get("xesam:title", "Unknown Title")
    song_artist = metadata.get("xesam:artist", "Unknown Artist")[0]
    song_length = round(metadata.get("mpris:length") / 1000000)
    cover_path = urllib.parse.urlparse(metadata.get("mpris:artUrl")).path

    return song_title, song_artist, song_length, cover_path


def get_position(player) -> int:
    bus = DBusSession.get_bus()
    player = bus.get_object(player,
                            "/org/mpris/MediaPlayer2")
    properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")
    position = properties.Get("org.mpris.MediaPlayer2.Player", "Position")

    return round(position / 1000000)


def get_state(player) -> str:
    bus = DBusSession.get_bus()
    player = bus.get_object(player,
                            "/org/mpris/MediaPlayer2")
    properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")
    state = properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
    return state


def get_trackid(player) -> str:
    bus = DBusSession.get_bus()
    player = bus.get_object(player,
                            "/org/mpris/MediaPlayer2")
    properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")

    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    trackid = metadata.get("mpris:trackid")

    return trackid
