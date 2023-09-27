import time, board, digitalio, audiomixer, analogio, neopixel, asyncio
from audiocore import WaveFile
from adafruit_ticks import ticks_ms, ticks_add, ticks_less, ticks_diff
import queue


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
btn1 = digitalio.DigitalInOut(board.GP27)
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
btn8 = digitalio.DigitalInOut(board.GP3)
btn8.switch_to_input(pull=digitalio.Pull.UP)
led8 = digitalio.DigitalInOut(board.GP2)
led8.direction = digitalio.Direction.OUTPUT

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
pixels[0] = (10, 100, 20)

current_btn_value = 1
prev_value = 1

pot1 = analogio.AnalogIn(board.GP28_A2)  # to read it: pot1.value 0 to 65535
pot1_value = 0
pot1 = analogio.AnalogIn(board.GP29_A3)  # to read it: pot1.value 0 to 65535

btns = [btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8]
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
mode = 0  # 0=play,1=sound,2=sequence,3=layer
play = True
btn1_debounce = True
i = 0

audio.play(mixer)


def wait(time):
    deadline = ticks_add(ticks_ms(), time)
    while ticks_less(ticks_ms(), deadline):
        pass


def truncate_float(float_number, decimal_places):
    multiplier = 10 ** decimal_places
    return int(float_number * multiplier) / multiplier


def play_sound(mixer_voice, ssound):
    mixer.voice[mixer_voice].play(ssound)


def set_led(index, vvalue):
    leds[index].value = vvalue


def play_sound_and_light(ss, i):
    mixer.voice[i].play(ss)
    leds[i].value = True
    deadline = ticks_add(ticks_ms(), bpm_millis)
    while ticks_less(ticks_ms(), deadline):
        pass
    leds[i].value = False


def mapp(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


async def play_sound_async(delay, mixer_voice, ssound):
    while True:
        mixer.voice[mixer_voice].play(ssound)
        await asyncio.sleep(
            delay
        )  # ogni quanto la funzione viene eseguita, lo "sleep" fa fare yeald e rilascia la cpu


async def play_sound_and_light_async(delay, sound, mixer_voice, sequence, q):
    a = 0
    while play:
        if not q.empty():
            delay = await q.get()
        if a > 7:
            a = 0
        if a == 0:
            leds[7].value = False
        if a != 0:
            leds[a - 1].value = False
        if sequence[a] == 1:
            mixer.voice[mixer_voice].play(sound)
            leds[a].value = True
        a += 1

        await asyncio.sleep(delay)  # yeald

async def play_async(delay, sound1,sound2,sound3, mixer_voice1,mixer_voice2,mixer_voice3, sequence1,sequence2,sequence3, q):
    a = 0
    while play:
        if not q.empty():
            delay = await q.get()
        if a > 7:
            a = 0
        if a == 0:
            leds[7].value = False
        if a != 0:
            leds[a - 1].value = False
        if sequence1[a] == 1:
            mixer.voice[mixer_voice1].play(sound1)
            leds[a].value = True
        if sequence2[a] == 1:
            mixer.voice[mixer_voice2].play(sound2)
            leds[a].value = True
        if sequence3[a] == 1:
            mixer.voice[mixer_voice3].play(sound3)
            leds[a].value = True
        a += 1

        await asyncio.sleep(delay)  # yeald

def set_led_async(index, vvalue):
    leds[index].value = vvalue


async def update_pot_value_async(delay):
    pot1_value = mapp(pot1.value, 65535, 0, 0, 65535)
    if pot1_value < 13107:
        mode = 0  # play
        pixels[0] = (10, 100, 20)
    elif pot1_value < 26214:
        mode = 1  # sound
        pixels[0] = (10, 200, 20)
    elif pot1_value < 39321:
        mode = 2  # pattern
    elif pot1_value < 52428:
        mode = 3
        pixels[0] = (100, 30, 20)
    else:
        pixels[0] = (10, 100, 100)
        mode = 4
    # TODO: add MODE t
    await asyncio.sleep(delay)


async def btn1_async(delay):  # TODO: check if it works
    prev_value = current_btn_value
    current_btn_value = btn1.value
    if current_btn_value == 0 and current_btn_value != prev_value:  # button is pressed
        current_btn_value = 1
        if mode == 0:
            play = not play
        elif mode == 1:
            sequence1[0] = not sequence1[0]
    await asyncio.sleep(delay)


async def main():
    q = queue.Queue()
#     asyncio.create_task(play_sound_and_light_async(bpm_float, kick, 0, sequence1, q))
#     asyncio.create_task(play_sound_and_light_async(bpm_float, snare, 1, sequence2, q))
#     asyncio.create_task(play_sound_and_light_async(bpm_float, hihat, 2, sequence3, q))

    asyncio.create_task(play_async(bpm_float,kick,snare,hihat,0,1,2,sequence1,sequence2,sequence3,q))

    # asyncio.create_task(update_pot_value_async(0.4))
    # asyncio.create_task(btn1_async(0.3)

    while True:
        pot1_value = mapp(pot1.value, 65535, 0, 0.05, 1)
        print(truncate_float(pot1_value, 1))
        await q.put(truncate_float(pot1_value, 1))
        pixels.show()
        await asyncio.sleep(0.3)


asyncio.run(main())
