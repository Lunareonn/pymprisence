from logs import logger
import asyncio
import presence
import configuration


async def main():
    await configuration.generate_config()

    event = asyncio.Event()
    RPC = await presence.initialize_rpc(event)
    asyncio.create_task(presence.rpc_loop(event, RPC))

    await asyncio.Future()

if __name__ == "__main__":
    logger.debug("Starting...")
    asyncio.run(main())
