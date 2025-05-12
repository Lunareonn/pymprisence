from pypresence import Presence, ActivityType
from gi.repository import GLib
from signal_handler import listener
import asyncio
import presence


async def main():
    event = asyncio.Event()
    RPC = await presence.initialize_rpc(event)
    asyncio.create_task(presence.rpc_loop(event, RPC))

    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
