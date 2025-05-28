from logs import logger
import asyncio
import presence
import configuration
import util
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--players", help="List available MPRIS players", action="store_true")
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

    await configuration.generate_config()

    event = asyncio.Event()
    RPC = await presence.initialize_rpc(event)
    asyncio.create_task(presence.rpc_loop(event, RPC))

    await asyncio.Future()

if __name__ == "__main__":
    logger.debug("Starting...")
    asyncio.run(main())
