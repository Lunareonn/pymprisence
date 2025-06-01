from configuration import config_folder
from dbus_connection import DBusSession
from diskcache import Cache
from logs import logger
import dbus
import base64
import urllib.parse
import json
import tomllib
import xxhash
import os
import aiohttp
import re

home_folder = os.path.expanduser("~")
os.makedirs(os.path.join(home_folder, ".pymprisence", "cache"), exist_ok=True)


def sanitize_player_name(player: str) -> str:
    player = player.replace("org.mpris.MediaPlayer2.", "")
    sanitized_player = re.sub(r"\..*$", "", player)
    logger.debug(f"Sanitized name from {player} to {sanitized_player}")
    return sanitized_player


async def get_players() -> list:
    bus = DBusSession.get_bus()
    names = bus.list_names()
    if names is None:
        return []

    players = [service for service in names if service.startswith("org.mpris.MediaPlayer2.")]
    logger.debug(f"Found {len(players)} players.")
    logger.debug(f"Players: {players}")
    return players


async def get_current_player() -> str | None:
    bus = DBusSession.get_bus()
    players = await get_players()

    for player in players:
        try:
            proxy = bus.get_object(player, "/org/mpris/MediaPlayer2")
            interface = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            status = interface.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")

            if check_if_ignored(player) is True or status in ["Stopped", "Paused"]:
                continue

            if status == "Playing":
                logger.debug(f"{player} is playing. Returning {player}")
                return player

        except dbus.DBusException as err:
            logger.error(err)
            continue

    logger.debug("No players were found.")
    return None


def check_if_ignored(player) -> bool:
    with open(os.path.join(config_folder, "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)

    sanitized_player = sanitize_player_name(player)

    try:
        if cfg_file["player"][sanitized_player]["ignore"] is True:
            logger.debug(f"{sanitized_player} is ignored.")
            return True
    except KeyError:
        if cfg_file["player"]["default"]["ignore"] is True:
            logger.debug(f"{sanitized_player} not found in config. Using default ignore value.")
            return True
        else:
            logger.debug(f"{sanitized_player} is not ignored.")
            return False

    logger.debug(f"{sanitized_player} is not ignored.")
    return False


async def cache_cover(file: str, url: str):
    cache = Cache(os.path.join(home_folder, ".pymprisence", "cache"))
    hasher = xxhash.xxh64()
    with open(str(file), "rb") as f:
        while chunk := f.read(1048576):
            hasher.update(chunk)
    logger.debug(f"Hashed cover. Cover hash: {hasher.hexdigest()}")

    data_json = {
        "cover_url": url
    }
    cache.set(hasher.hexdigest(), json.dumps(data_json))
    logger.debug(f"Cached hash. Cached data: {json.dumps(data_json)}")


async def clear_cache():
    cache = Cache(os.path.join(home_folder, ".pymprisence", "cache"))
    cleared = cache.clear()
    if cleared == 0:
        print("Nothing to clear.")
        return
    print(f"Cleared {cleared} items from cache.")


async def upload_imgbb(file: str, track: str, artist: str) -> str | None:
    with open(os.path.join(config_folder, "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)

    api_key = cfg_file["cover_art"]["imgbb_api_key"]
    url = "https://api.imgbb.com/1/upload"

    async with aiohttp.ClientSession() as session:
        with open(str(file), "rb") as img:
            payload = {
                "key": api_key,
                "image": base64.b64encode(img.read()).decode(),
            }

        logger.debug("Uploading cover to imgbb")
        async with session.post(url, data=payload) as response:
            if response.status == 400:
                logger.warning("Upload failed! 400 Bad Request from ImgBB. Check your API Key.")
                return None
            data = await response.json()
            logger.debug(f"Uploaded cover. {data["data"]["image"]["url"]}")
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

    logger.debug(f"Fetched metadata: {song_artist} - {song_title} ({song_length}s)")
    logger.debug(f"Cover path: {cover_path}")
    return song_title, song_artist, song_length, cover_path


def get_position(player) -> int:
    bus = DBusSession.get_bus()
    player = bus.get_object(player,
                            "/org/mpris/MediaPlayer2")
    properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")
    position = properties.Get("org.mpris.MediaPlayer2.Player", "Position")

    logger.debug(f"Fetched position: {position / 1000000}s")
    return round(position / 1000000)


def get_state(player) -> str:
    bus = DBusSession.get_bus()
    player = bus.get_object(player,
                            "/org/mpris/MediaPlayer2")
    properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")
    state = properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")

    logger.debug(f"Fetched player state: {state}")
    return state


def get_trackid(player) -> str:
    bus = DBusSession.get_bus()
    player = bus.get_object(player,
                            "/org/mpris/MediaPlayer2")
    properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")

    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    trackid = metadata.get("mpris:trackid")

    logger.debug(f"Fetched trackid: {trackid}")
    return trackid
