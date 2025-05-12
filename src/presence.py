from pypresence import AioPresence, ActivityType
from pathlib import Path
import asyncio
import util
import time
import diskcache
import json
import xxhash


async def initialize_rpc(event):
    client_id = "1366680558775570504"
    RPC = AioPresence(client_id)
    await RPC.connect()
    print("connected rpc")
    event.set()
    return RPC


async def rpc_loop(event, RPC):
    await event.wait()
    while True:
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
