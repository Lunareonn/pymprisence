from pypresence.presence import AioPresence
from pypresence.types import ActivityType
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


async def initialize_rpc(event):
    with open(os.path.join(config_folder, "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)
    app_id = cfg_file["discord"]["app_id"]
    RPC = AioPresence(app_id)
    await RPC.connect()
    logger.info("RPC Initialized")
    event.set()
    return RPC


async def rpc_loop(event, RPC):
    await event.wait()
    last_song = None

    while True:
        player = await util.get_current_player()
        if player is None:
            await asyncio.sleep(5)
            continue

        current_song = util.get_trackid(player)
        if current_song == last_song:
            await asyncio.sleep(5)
            continue

        last_song = current_song

        state = util.get_state(player)
        if state in ["Paused", "Stopped"]:
            await RPC.clear()
            await asyncio.sleep(5)
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

        await RPC.update(details=song_title,
                         state=song_artist,
                         large_image=cover_url,
                         start=time.time() - position,
                         end=time.time() + int(song_length) - position,
                         activity_type=ActivityType.LISTENING)
        logger.info(f"Updated RPC to {song_artist} - {song_title}")
        await asyncio.sleep(5)
