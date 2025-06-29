from logs import logger
from signal_handler import init_listener_thread
import asyncio
import presence
import configuration
import util
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--players", help="List available MPRIS players", action="store_true")
    parser.add_argument("--clear-cache", help="Clear ImgBB link cache.", action="store_true")
    args = parser.parse_args()

    return args


async def main():
    args = parse_args()

    if args.players:
        players = await util.get_players()
        print("Available players:")
        for player in players:
            sanitized_player = util.sanitize_player_name(player)
            print("-", sanitized_player)
        sys.exit(0)
    if args.clear_cache:
        await util.clear_cache()
        sys.exit(0)

    await init_listener_thread()
    await configuration.generate_config()

    RPC = await presence.wait_for_discord()
    asyncio.create_task(presence.rpc_loop(RPC))

    await asyncio.Future()

if __name__ == "__main__":
    logger.debug("Starting...")
    asyncio.run(main())
