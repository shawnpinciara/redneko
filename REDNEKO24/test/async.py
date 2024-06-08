import asyncio

async def btn1_async(delay):
    while True:
        #do stuff
        print()
    await asyncio.sleep(delay)


async def main():
    asyncio.create_task(btn1_async(0.4))