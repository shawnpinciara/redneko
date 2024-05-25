import time
import board 
import digitalio
import audiomixer
import analogio
import neopixel
import asyncio

from adafruit_ticks import ticks_ms, ticks_add, ticks_less, ticks_diff
import queue
import pattern
import obj
import btn
import async_button
import synth_engine as s

bpm = 400
bpm_millis = int((60 * 1000) / bpm)
bpm_float = 60 / bpm


# I/O
btn1 = async_button.SimpleButton(board.GP27, value_when_pressed=False)
led1 = digitalio.DigitalInOut(board.GP26)
led1.direction = digitalio.Direction.OUTPUT

btn2 = async_button.SimpleButton(board.GP15, value_when_pressed=False)
led2 = digitalio.DigitalInOut(board.GP14)
led2.direction = digitalio.Direction.OUTPUT

btn3 = async_button.SimpleButton(board.GP13, value_when_pressed=False)
led3 = digitalio.DigitalInOut(board.GP12)
led3.direction = digitalio.Direction.OUTPUT

btn4 = async_button.SimpleButton(board.GP11, value_when_pressed=False)
led4 = digitalio.DigitalInOut(board.GP10)
led4.direction = digitalio.Direction.OUTPUT

btn5 = async_button.SimpleButton(board.GP9, value_when_pressed=False)
led5 = digitalio.DigitalInOut(board.GP8)
led5.direction = digitalio.Direction.OUTPUT

btn6 = async_button.SimpleButton(board.GP7, value_when_pressed=False)
led6 = digitalio.DigitalInOut(board.GP6)
led6.direction = digitalio.Direction.OUTPUT

btn7 = async_button.SimpleButton(board.GP5, value_when_pressed=False)
led7 = digitalio.DigitalInOut(board.GP4)
led7.direction = digitalio.Direction.OUTPUT

btn8 = async_button.SimpleButton(board.GP3, value_when_pressed=False)
led8 = digitalio.DigitalInOut(board.GP2)
led8.direction = digitalio.Direction.OUTPUT

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
pixels[0] = (10, 100, 20)

current_btn_value = 1
prev_value = 1

pot1 = analogio.AnalogIn(board.GP29_A3)  # to read it: pot1.value 0 to 65535
pot1_value = 0
pot2 = analogio.AnalogIn(board.GP28_A2)  # to read it: pot1.value 0 to 65535
pot2_value = 0

btns = [btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8]
leds = [led1, led2, led3, led4, led5, led6, led7, led8]
midi_values = [0,1,2,3,4,5,6,7,8,9,10,11]
octave = 4
maj7_arr = [0,4,7,11]
min7_arr = [0,3,7,10]
dom7_arr = [0,4,7,10]

maj1_arr = [0,4,7,11]
minor2_arr = [-2,0,3,7]
minor3_arr = [-2,0,3,7]
maj4_arr = [-5,-1,0,4]
dom5_arr = [-5,-2,0,4]
minor6_arr = [-9,-5,-2,0]
dim7_arr = [-9,-6,-2,0]

s_note = 60


btn1_debounce = True

def mapp(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

async def main():

    #HANDLE BUTTONS
    asyncio.create_task(s.play_chord_async(0.3,btns[0],leds[0],60,maj7_arr))
    asyncio.create_task(s.play_chord_async(0.3,btns[1],leds[1],62,minor2_arr))
    asyncio.create_task(s.play_chord_async(0.3,btns[2],leds[2],64,minor3_arr))
    #asyncio.create_task(play_chord_async(0.3,btns[3],leds[3],65,maj4_arr))   ERROR ARISE HERE
    asyncio.create_task(s.play_chord_async(0.3,btns[4],leds[4],67,dom5_arr))
    asyncio.create_task(s.play_chord_async(0.3,btns[5],leds[5],69,minor6_arr))
    asyncio.create_task(s.play_chord_async(0.3,btns[6],leds[6],71,dim7_arr))

    asyncio.create_task(s.stop_play_async(0.3,btns[7]))


    while True:
#         mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4
        pot1_value = mapp(pot1.value, 66535, 0, 0.1, 1.5)
        pot2_value = mapp(pot2.value, 65535, 0, 0, 10)
        #wavetable1.set_wave_pos(int(pot2_value)*2)
        await asyncio.sleep(0.2)


asyncio.run(main())
