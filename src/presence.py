from pypresence import AioPresence, ActivityType
import asyncio


async def initialize_rpc():
    client_id = "1366680558775570504"
    RPC = AioPresence(client_id)
    await RPC.connect()
    print("connected rpc")

    await RPC.update(details="test")


async def rpc_loop():
    while True:
        print("hi")
        await asyncio.sleep(5)
