from pypresence.presence import AioPresence
from pypresence.types import ActivityType
from pypresence.exceptions import DiscordNotFound, PipeClosed
from configuration import config_folder
from pathlib import Path
from logs import logger
import asyncio
import util
import time
import diskcache
import json
import xxhash
import tomllib
import os


async def initialize_rpc():
    with open(os.path.join(config_folder, "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)
    app_id = cfg_file["discord"]["app_id"]
    RPC = AioPresence(app_id)

    try:
        await RPC.connect()
    except DiscordNotFound:
        logger.warning("Discord wasn't found! Waiting like a good boy...")
        return None

    logger.info("RPC Initialized")
    return RPC


async def wait_for_discord():
    while True:
        RPC = await initialize_rpc()
        if RPC:
            return RPC

        await asyncio.sleep(5)


async def rpc_loop(RPC):
    with open(os.path.join(config_folder, "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)

    last_song = None
    interval = cfg_file["discord"]["interval"]
    if interval < 5:
        interval = 5

    activity_type_map = {
        "listening": ActivityType.LISTENING,
        "watching": ActivityType.WATCHING,
        "competing": ActivityType.COMPETING,
        "playing": ActivityType.PLAYING,
    }

    while True:
        player = await util.get_current_player()
        if player is None:
            await asyncio.sleep(interval)
            continue
        sanitized_player = util.sanitize_player_name(player)

        activity_type = activity_type_map.get(cfg_file["player"][sanitized_player]["activity_type"], None)
        if activity_type is None:
            activity_type = activity_type_map.get(cfg_file["player"]["default"]["activity_type"])

        current_song = util.get_trackid(player)
        if current_song == last_song:
            await asyncio.sleep(interval)
            continue

        last_song = current_song

        state = util.get_state(player)
        if state in ["Paused", "Stopped"]:
            await RPC.clear()
            await asyncio.sleep(interval)
            continue

        song_title, song_artist, song_length, cover_path = util.get_metadata(player)
        position = util.get_position(player)

        file_hash = xxhash.xxh64(Path(cover_path).read_bytes()).hexdigest()
        cache = diskcache.Cache("./cache")
        if file_hash in cache:
            logger.debug("Fetching cover from cache.")
            data = json.loads(str(cache.get(file_hash)))
            cover_url = data.get("cover_url")
        else:
            uploader_task = asyncio.create_task(util.upload_imgbb(
                cover_path, song_title, song_artist))
            cover_url = await uploader_task

        try:
            await RPC.update(details=song_title,
                             state=song_artist,
                             large_image=cover_url,
                             start=time.time() - position,
                             end=time.time() + int(song_length) - position,
                             activity_type=activity_type)
        except PipeClosed:
            await wait_for_discord()
        logger.info(f"Updated RPC to {song_artist} - {song_title} (Player: {player})")
        await asyncio.sleep(interval)
