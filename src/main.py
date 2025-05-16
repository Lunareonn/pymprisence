import asyncio
import presence
import configuration
import util


async def main():
    event = asyncio.Event()
    players = await util.get_players()
    print("players:")
    for player in players:
        print(player)
    RPC = await presence.initialize_rpc(event)
    asyncio.create_task(presence.rpc_loop(event, RPC))

    await configuration.generate_config()
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
