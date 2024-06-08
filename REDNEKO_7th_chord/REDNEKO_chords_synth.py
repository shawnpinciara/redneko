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
import adafruit_wave
import ulab.numpy as np
import random


bpm = 400
bpm_millis = int((60 * 1000) / bpm)
bpm_float = 60 / bpm


# I/O
btn1 = async_button.Button(board.GP27, value_when_pressed=False)
led1 = digitalio.DigitalInOut(board.GP26)
led1.direction = digitalio.Direction.OUTPUT

btn2 = async_button.Button(board.GP15, value_when_pressed=False)
led2 = digitalio.DigitalInOut(board.GP14)
led2.direction = digitalio.Direction.OUTPUT

btn3 = async_button.Button(board.GP13, value_when_pressed=False)
led3 = digitalio.DigitalInOut(board.GP12)
led3.direction = digitalio.Direction.OUTPUT

btn4 = async_button.Button(board.GP11, value_when_pressed=False)
led4 = digitalio.DigitalInOut(board.GP10)
led4.direction = digitalio.Direction.OUTPUT

btn5 = async_button.Button(board.GP9, value_when_pressed=False)
led5 = digitalio.DigitalInOut(board.GP8)
led5.direction = digitalio.Direction.OUTPUT

btn6 = async_button.Button(board.GP7, value_when_pressed=False)
led6 = digitalio.DigitalInOut(board.GP6)
led6.direction = digitalio.Direction.OUTPUT

btn7 = async_button.Button(board.GP5, value_when_pressed=False)
led7 = digitalio.DigitalInOut(board.GP4)
led7.direction = digitalio.Direction.OUTPUT

btn8 = async_button.Button(board.GP3, value_when_pressed=False)
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
octave = 4
s = 64
midi_values = [0,1,2,3,4,5,6,7,8,9,10,11]
midi_scale_array = [s,s+2,s+4,s+5,s+7,s+9,s+11]
maj7_arr = [0,4,7,11]
min7_arr = [0,3,7,10]
dom7_arr = [0,4,7,10]
dim7_arr = [0,3,6,9]

major1_arr = [0,4,7,11]
minor2_arr = [-2,0,3,7]
minor3_arr = [-2,0,3,7]
major4_arr = [-5,-1,0,4]
dominant5_arr = [-5,-2,0,4]
minor6_arr = [-9,-5,-2,0]
diminished7_arr = [-9,-6,-2,0]

chords_array = [maj7_arr,min7_arr,min7_arr,maj7_arr,dom7_arr,min7_arr,dim7_arr]
chords_array_inverseions = [major1_arr,minor2_arr,minor2_arr,major4_arr,dominant5_arr,minor6_arr,diminished7_arr]

s_note = 60

# SOUNDS:
# from https://waveeditonline.com/
#https://kimurataro.bandcamp.com/album/free-wavetables
wavetable_fname = "wav/1.WAV"
wavetable_sample_size = 256  # number of samples per wave in wavetable (256 is standard)
sample_rate = 25000
wave_lfo_min = 0  # which wavetable number to start from
wave_lfo_max = 10  # which wavetable number to go up to

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
mixer.voice[0].level = 0.5

btn1_debounce = True

def lerp(a, b, t):  return (1-t)*a + t*b

class Wavetable:
    """ A 'waveform' for synthio.Note that uses a wavetable w/ a scannable wave position."""
    def __init__(self, filepath, wave_len=256):
        self.w = adafruit_wave.open(filepath)
        self.wave_len = wave_len  # how many samples in each wave
        if self.w.getsampwidth() != 2 or self.w.getnchannels() != 1:
            raise ValueError("unsupported WAV format")
        self.waveform = np.zeros(wave_len, dtype=np.int16)  # empty buffer we'll copy into
        self.num_waves = self.w.getnframes() // self.wave_len
        self.set_wave_pos(0)

    def set_wave_pos(self, pos):
        """Pick where in wavetable to be, morphing between waves"""
        pos = min(max(pos, 0), self.num_waves-1)  # constrain
        samp_pos = int(pos) * self.wave_len  # get sample position
        self.w.setpos(samp_pos)
        waveA = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        self.w.setpos(samp_pos + self.wave_len)  # one wave up
        waveB = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        pos_frac = pos - int(pos)  # fractional position between wave A & B
        self.waveform[:] = lerp(waveA, waveB, pos_frac) # mix waveforms A & B


wavetable1 = Wavetable(wavetable_fname, wave_len=wavetable_sample_size)
wavetable1.set_wave_pos(0)
amp_env = synthio.Envelope(sustain_level=0.8, attack_time=0.05, release_time=0.5)
wave_lfo = synthio.LFO(rate=0.1, waveform=np.array((0,32767), dtype=np.int16) )
lpf = synth.low_pass_filter(4000, 1)  # cut some of the annoying harmonics

synth.blocks.append(wave_lfo)  # attach wavelfo to global lfo runner since cannot attach to note


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

async def play_chord_async(delay,button,led,s_note,chord_arr):
    while True:
        await button.wait(1) #https://circuitpython-async-button.readthedocs.io/en/latest/api.html#async_button.MultiButton
        synth.release_all()

        #bass root
        f = synthio.midi_to_hz(s_note-36) # + random.uniform(-0.1,0.1) )
        lpf = synth.low_pass_filter(4000, 1)  # cut some of the annoying harmonics
        vibrato_lfo = synthio.LFO(rate=1, scale=0.01)
        note = synthio.Note( frequency=f, waveform=wavetable1.waveform,envelope=amp_env, filter=lpf, bend=vibrato_lfo )
        synth.press(note)

        #7t chord
        f = synthio.midi_to_hz(s_note) # + random.uniform(-0.1,0.1) )
        lpf = synth.low_pass_filter(f+100, 1)  # cut some of the annoying harmonics
        for i in range(0,4):
            f = synthio.midi_to_hz(s_note+chord_arr[i]-(random.randint(0,1)*12)) + random.uniform(-0.1,0.1)
            note = synthio.Note( frequency=f, waveform=wavetable1.waveform,envelope=amp_env, filter=lpf, bend=vibrato_lfo )
            synth.press(note)
        pixels[0] = (random.randint(0,120), 100, 20)
        pixels.show()
        led.value = True
        await button.wait(2)
        led.value = False
    await asyncio.sleep(delay)

async def stop_play_async(delay,button):
    while True:
        await button.wait(1)
        synth.release_all()
    await asyncio.sleep(delay)

async def main():



    #HANDLE BUTTONS
    asyncio.create_task(play_chord_async(0.3,btns[0],leds[0],60,maj7_arr))
    asyncio.create_task(play_chord_async(0.3,btns[1],leds[1],62,minor2_arr))
    asyncio.create_task(play_chord_async(0.3,btns[2],leds[2],64,minor3_arr))
    #asyncio.create_task(play_chord_async(0.3,btns[3],leds[3],65,maj4_arr))   ERROR ARISE HERE
    asyncio.create_task(play_chord_async(0.3,btns[4],leds[4],67,dom5_arr))
    asyncio.create_task(play_chord_async(0.3,btns[5],leds[5],69,minor6_arr))
    asyncio.create_task(play_chord_async(0.3,btns[6],leds[6],71,dim7_arr))

    asyncio.create_task(stop_play_async(0.3,btns[7]))


    while True:
#         mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4
        pot1_value = mapp(pot1.value, 66535, 0, 0, 1)
        pot2_value = mapp(pot2.value, 65535, 0, 0, 10)
        wavetable1.set_wave_pos(int(pot2_value)*2)
        mixer.voice[0].level = pot1_value
        await asyncio.sleep(0.2)


asyncio.run(main())
