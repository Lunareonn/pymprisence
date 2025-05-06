from pypresence import Presence, ActivityType
from gi.repository import GLib
from signal_handler import listener
import asyncio
import time
import util

client_id = "1366680558775570504"
RPC = Presence(client_id)
RPC.connect()

song_title, song_artist, song_length = util.get_metadata()
position = util.get_position()

RPC.update(
    activity_type=ActivityType.LISTENING,
    details=song_title,
    state=song_artist,
    start=time.time() - position,
    end=int(song_length) + time.time() - position,
)

asyncio.run(listener())
loop = GLib.MainLoop()
loop.run()

while True:
    time.sleep(5)
    position = util.get_position()
    start_time = time.time() - position
    RPC.update(
        activity_type=ActivityType.LISTENING,
        details=song_title,
        state=song_artist,
        start=time.time() - position,
        end=time.time() + int(song_length) - position,
    )
