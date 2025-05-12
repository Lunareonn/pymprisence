from pypresence import Presence, ActivityType
from gi.repository import GLib
from signal_handler import listener
import asyncio
import presence


async def main():
    event = asyncio.Event()
    RPC = await presence.initialize_rpc(event)
    await presence.rpc_loop(event, RPC)

if __name__ == "__main__":
    asyncio.run(main())
