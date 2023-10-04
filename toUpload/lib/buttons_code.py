async def btn_async_mode_0(delay,button,patterns,mode,play):
    while True:
        await button.pressed()
        if mode.get() == 0:
            play.set(True)
        else:
            patterns[0].set(0,1)
    await asyncio.sleep(delay)


