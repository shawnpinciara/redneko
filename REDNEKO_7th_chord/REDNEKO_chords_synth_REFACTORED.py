import time
import board
import digitalio
import audiomixer
import analogio
import asyncio

from adafruit_ticks import ticks_ms, ticks_add, ticks_less, ticks_diff
import queue
import pattern
import obj
import btn
import async_button
import synth_engine as s
import touchio
from adafruit_debouncer import Debouncer, Button # type: ignore


bpm = 400
bpm_millis = int((60 * 1000) / bpm)
bpm_float = 60 / bpm


# I/O

current_btn_value = 1
prev_value = 1

pot1 = analogio.AnalogIn(board.GP29_A3)  # to read it: pot1.value 0 to 65535
pot1_value = 0
pot2 = analogio.AnalogIn(board.GP28_A2)  # to read it: pot1.value 0 to 65535
pot2_value = 0
btn1_debounce = True

def mapp(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

THRESHOLD = 1000
t = touchio.TouchIn(board.GP21)
t.threshold = t.raw_value + THRESHOLD
touchpad = Button(t, value_when_pressed=True)

async def scan_buttons():
    global touchpad
    while True:
        touchpad.update()
        if touchpad.rose:
            print("Touch On")
        if touchpad.fell:
            print("Touch Off")
    await asyncio.sleep(0.1)

async def main():

    #HANDLE BUTTONS
    asyncio.create_task(scan_buttons())


    #while True:
#         mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4
        #pot1_value = mapp(pot1.value, 66535, 0, 0.1, 1.5)
        #pot2_value = mapp(pot2.value, 65535, 0, 0, 10)
        #wavetable1.set_wave_pos(int(pot2_value)*2)
        #await asyncio.sleep(0.2)


asyncio.run(main())
