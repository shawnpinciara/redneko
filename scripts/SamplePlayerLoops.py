import time, board, digitalio, audiomixer, analogio, neopixel, asyncio
from audiocore import WaveFile
from adafruit_ticks import ticks_ms, ticks_add, ticks_less, ticks_diff
import queue
import pattern
import obj
import btn
import async_button


try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!
# VARIABLES
bpm = 400
bpm_millis = int((60 * 1000) / bpm)
bpm_float = 60 / bpm


# I/O
btn1 = digitalio.DigitalInOut(board.GP3)
btn1.switch_to_input(pull=digitalio.Pull.UP)
led1 = digitalio.DigitalInOut(board.GP26)
led1.direction = digitalio.Direction.OUTPUT
btn2 = digitalio.DigitalInOut(board.GP15)
btn2.switch_to_input(pull=digitalio.Pull.UP)
led2 = digitalio.DigitalInOut(board.GP14)
led2.direction = digitalio.Direction.OUTPUT
btn3 = digitalio.DigitalInOut(board.GP13)
btn3.switch_to_input(pull=digitalio.Pull.UP)
led3 = digitalio.DigitalInOut(board.GP12)
led3.direction = digitalio.Direction.OUTPUT
btn4 = digitalio.DigitalInOut(board.GP11)
btn4.switch_to_input(pull=digitalio.Pull.UP)
led4 = digitalio.DigitalInOut(board.GP10)
led4.direction = digitalio.Direction.OUTPUT
btn5 = digitalio.DigitalInOut(board.GP9)
btn5.switch_to_input(pull=digitalio.Pull.UP)
led5 = digitalio.DigitalInOut(board.GP8)
led5.direction = digitalio.Direction.OUTPUT
btn6 = digitalio.DigitalInOut(board.GP7)
btn6.switch_to_input(pull=digitalio.Pull.UP)
led6 = digitalio.DigitalInOut(board.GP6)
led6.direction = digitalio.Direction.OUTPUT
btn7 = digitalio.DigitalInOut(board.GP5)
btn7.switch_to_input(pull=digitalio.Pull.UP)
led7 = digitalio.DigitalInOut(board.GP4)
led7.direction = digitalio.Direction.OUTPUT
# btn8 = digitalio.DigitalInOut(board.GP3)
# btn8.switch_to_input(pull=digitalio.Pull.UP)
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

btns = [btn1, btn2, btn3, btn4, btn5, btn6, btn7]
leds = [led1, led2, led3, led4, led5, led6, led7, led8]


# SOUNDS:
loop = WaveFile(open("/loops/1/loop.wav", "rb"))
loop1 = WaveFile(open("/loops/1/loop1.wav", "rb"))
loop2 = WaveFile(open("/loops/1/loop2.wav", "rb"))
loop3 = WaveFile(open("/loops/1/loop3.wav", "rb"))
loop4 = WaveFile(open("/loops/1/loop4.wav", "rb"))
kick = WaveFile(open("/loops/todbot/kick.wav", "rb"))
hihat = WaveFile(open("/loops/todbot/hihat.wav", "rb"))
snare = WaveFile(open("/loops/todbot/snare.wav", "rb"))

# MIXER (OUTS)
mixer = audiomixer.Mixer(
    voice_count=4,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)
audio = AudioOut(board.GP0)
audio.play(mixer)

# PROGRAM VARIABLES
sequence1 = [1,0,0,0,1,1,0,0]  # kick
sequence2 = [0,0,1,0,0,0,1,0]  # snare
sequence3 = [1,1,0,1,1,1,0,1]  # hihat
#mode = 0  # 0=play,1=sound,2=sequence,3=layer
btn1_debounce = True
i = 0

audio.play(mixer)


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

async def play_async_obj(delay, sound1,sound2,sound3, mixer_voice1,mixer_voice2,mixer_voice3, sequence1,sequence2,sequence3, q,play):
    a = 0
    while play.get():
        if not q.empty():
            delay = await q.get()
        if a > 7:
            a = 0
        if a == 0:
            leds[7].value = False
        if a != 0:
            leds[a - 1].value = False
        #use getter and setter
        if sequence1.get(a) == 1:
            mixer.voice[mixer_voice1].play(sound1)
            leds[a].value = True
        if sequence2.get(a) == 1:
            mixer.voice[mixer_voice2].play(sound2)
            leds[a].value = True
        if sequence3.get(a) == 1:
            mixer.voice[mixer_voice3].play(sound3)
            leds[a].value = True
        a += 1
        await asyncio.sleep(delay)  # yeald


async def btn_async_mode_0(delay,button,patterns,mode,play):  # TODO: check if it works
    while True:
        await button.pressed()
        if mode.get() == 0:
            play.set(True)
        else:
            patterns[0].set(0,1)
    await asyncio.sleep(delay)


async def main():
    q = queue.Queue()
    btn1_queue = queue.Queue()
    mode = obj.Obj()
    play = obj.Obj()
    play.set(True)
    #btn_obj = btn.Btn()
    button = async_button.SimpleButton(board.GP27, value_when_pressed=False)

    pat1 = pattern.Pattern()
    pat1.set_array([1,0,0,0,1,1,0,0])

    pat2 = pattern.Pattern()
    pat2.set_array([0,0,1,0,0,0,1,0])

    pat3 = pattern.Pattern()
    pat3.set_array([1,1,0,1,1,1,0,1])

    pat1.set(0,0)
    pat2.set(0,0)
    pat3.set(0,0)
    patterns = [pat1,pat2,pat3]

    asyncio.create_task(play_async_obj(bpm_float,kick,snare,hihat,0,1,2,pat1,pat2,pat3,q,play))
    asyncio.create_task(btn_async_mode_0(0.4,button,patterns,mode,play))


    while True:
        pot1_value = mapp(pot1.value, 66535, 0, 0.1, 1.5)
        pot2_value = mapp(pot2.value, 65535, 0, 0, 65535)
        await btn1_queue.put(btn1.value)
        await q.put(truncate_float(pot1_value, 1))
        if pot2_value < 13107:
            mode.set(0)  # play
            pixels[0] = (10, 100, 20)
        elif pot2_value < 26214:
            mode.set(1)  # sound
            pixels[0] = (10, 200, 0)
        elif pot2_value < 39321:
            mode.set(2)  # pattern
        elif pot2_value < 52428:
            mode.set(3)
            pixels[0] = (100, 30, 20)
        else:
            pixels[0] = (10, 100, 100)
            mode.set(4)
        pixels.show()
        await asyncio.sleep(0.4)


asyncio.run(main())