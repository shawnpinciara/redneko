import time, board, digitalio, audiomixer, analogio, neopixel, asyncio
from audiocore import WaveFile
from adafruit_ticks import ticks_ms, ticks_add, ticks_less, ticks_diff
import queue
import pattern
import obj
import btn
import async_button
import synthio
import audiopwmio


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
minor7_arr = [0,3,7,10]
dom7_arr = [0,4,7,10]
s_note = 60

# SOUNDS:

# MIXER (OUTS)
audio = audiopwmio.PWMAudioOut(board.GP0)
mixer = audiomixer.Mixer(
    voice_count=4,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)
synth = synthio.Synthesizer(channel_count=1, sample_rate=22050)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 0.4

btn1_debounce = True


def truncate_float(float_number, decimal_places):
    multiplier = 10 ** decimal_places
    return int(float_number * multiplier) / multiplier

def mapp(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

async def btn1_async(delay,button,s_note):
    while True:
        await button.pressed()
        for i in range(0,3):
            synth.press((s_note+maj7_arr[i]))
        await button.released()
        for i in range(0,3):
            synth.release((s_note+maj7_arr[i]))
    await asyncio.sleep(delay)

async def play_maj_async(delay,button,s_note):
    while True:
        await button.pressed()
        pixels[0] = (255, 255, 0)
        for i in range(0,3):
            synth.press((s_note+maj7_arr[i]))
        pixels.show()
        await button.released()
        for i in range(0,3):
            synth.release((s_note+maj7_arr[i]))
    await asyncio.sleep(delay)

async def play_minor_async(delay,button,s_note):
    while True:
        await button.pressed()
        pixels[0] = (0, 255, 0)
        for i in range(0,3):
            synth.press((s_note+minor7_arr[i]))
        pixels.show()
        await button.released()
        for i in range(0,3):
            synth.release((s_note+minor7_arr[i]))
    await asyncio.sleep(delay)

async def play_dom_async(delay,button,s_note):
    while True:
        await button.pressed()
        pixels[0] = (255, 0, 0) #green
        for i in range(0,3):
            synth.press((s_note+dom7_arr[i]))
        pixels.show()
        await button.released()
        for i in range(0,3):
            synth.release((s_note+dom7_arr[i]))
    await asyncio.sleep(delay)
async def main():
    #asyncio.create_task(play_async_obj(bpm_float,kick,snare,hihat,0,1,2,pat1,pat2,pat3,q,play)) #PLAY

    #HANDLE BUTTONS
    asyncio.create_task(play_maj_async(0.3,btns[0],60))
    asyncio.create_task(play_minor_async(0.3,btns[1],62))
    asyncio.create_task(play_minor_async(0.3,btns[2],64))
#     asyncio.create_task(btn1_async(0.3,btns[3],65))
    asyncio.create_task(play_dom_async(0.3,btns[4],67))
    asyncio.create_task(play_maj_async(0.3,btns[5],69))
    asyncio.create_task(play_maj_async(0.3,btns[6],71))



    # delay = 2
    while True:
#         mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4
        # pot1_value = mapp(pot1.value, 66535, 0, 0.1, 1.5)
#         pot2_value = mapp(pot2.value, 65535, 0, 0, 65535)
#         await q.put(truncate_float(pot1_value, 1))
#         if pot2_value < 13107:
#             mode.set(0)  # play
#             pixels[0] = (255, 0, 0) #green
#         elif pot2_value < 26214:
#             mode.set(2)  # pattern
#             pixels[0] = (0, 255, 0) #red
#         elif pot2_value < 39321:
#             mode.set(1)  # sound
#             pixels[0] = (0, 0, 255) #blue
#         elif pot2_value < 52428:
#             mode.set(3)
#             pixels[0] = (255, 255, 0) #yellow
#         else:
#             pixels[0] = (255, 255, 255) #white
#             mode.set(4)
#         pixels.show()
        await asyncio.sleep(0.4)


asyncio.run(main())
