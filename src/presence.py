from pypresence import AioPresence, ActivityType
from pathlib import Path
import asyncio
import util
import time
import diskcache
import json
import xxhash
from configuration import config_folder
import tomllib
import os


async def initialize_rpc(event):
    with open(os.path.join(config_folder, "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)
    app_id = cfg_file["discord"]["app_id"]
    RPC = AioPresence(app_id)
    await RPC.connect()
    print("connected rpc")
    event.set()
    return RPC


async def rpc_loop(event, RPC):
    await event.wait()
    last_song = None

    while True:
        current_song = util.get_trackid()
        if current_song == last_song:
            await asyncio.sleep(5)
            continue

        last_song = current_song

        state = util.get_state()
        if state in ["Paused", "Stopped"]:
            print(state)
            await RPC.clear()
            await asyncio.sleep(5)
            continue

        song_title, song_artist, song_length, cover_path = util.get_metadata()
        position = util.get_position()

        file_hash = xxhash.xxh64(Path(cover_path).read_bytes()).hexdigest()
        cache = diskcache.Cache("./cache")
        if file_hash in cache:
            print("fetching cover from cache")
            data = json.loads(cache.get(file_hash))
            cover_url = data.get("cover_url")
        else:
            print("uploading cover to imgbb")
            uploader_task = asyncio.create_task(util.upload_imgbb(
                cover_path, song_title, song_artist))
            cover_url = await uploader_task

        await RPC.update(details=song_title,
                         state=song_artist,
                         large_image=cover_url,
                         start=time.time() - position,
                         end=time.time() + int(song_length) - position,
                         activity_type=ActivityType.LISTENING)
        print("rpc updated")
        await asyncio.sleep(5)
