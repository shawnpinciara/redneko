# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials Audio Out WAV example"""
import time, board,digitalio,audiomixer
from audiocore import WaveFile
from adafruit_ticks import ticks_ms, ticks_add, ticks_less


try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!
#VARIABLES
bpm = 200
bpm_millis = int((60*1000)/bpm)


#INPUTS
btn1 = digitalio.DigitalInOut(board.GP27)
btn1.switch_to_input(pull=digitalio.Pull.UP)
led1 = digitalio.DigitalInOut(board.GP26)
led1.direction = digitalio.Direction.OUTPUT
btn2 = digitalio.DigitalInOut(board.GP15)
btn2.switch_to_input(pull=digitalio.Pull.UP)
led2 = digitalio.DigitalInOut(board.GP14)
led2.direction = digitalio.Direction.OUTPUT
btn3 = digitalio.DigitalInOut(board.GP8)
btn3.switch_to_input(pull=digitalio.Pull.UP)
led3 = digitalio.DigitalInOut(board.GP7)
led3.direction = digitalio.Direction.OUTPUT
btn4 = digitalio.DigitalInOut(board.GP6)
btn4.switch_to_input(pull=digitalio.Pull.UP)
led4 = digitalio.DigitalInOut(board.GP5)
led4.direction = digitalio.Direction.OUTPUT

btns = [btn1,btn2,btn3,btn4]
leds = [led1,led2,led3,led4]


#SOUNDS:
loop = WaveFile(open("/loops/1/loop.wav", "rb"))
loop1 = WaveFile(open("/loops/1/loop1.wav", "rb"))
loop2 = WaveFile(open("/loops/1/loop2.wav", "rb"))
loop3 = WaveFile(open("/loops/1/loop3.wav", "rb"))
loop4 = WaveFile(open("/loops/1/loop4.wav", "rb"))
kick = WaveFile(open("/loops/todbot/kick.wav", "rb"))
hihat = WaveFile(open("/loops/todbot/hihat.wav", "rb"))
snare = WaveFile(open("/loops/todbot/snare.wav", "rb"))

#MIXER (OUTS)
mixer = audiomixer.Mixer(voice_count=4, sample_rate=22050, channel_count=1,bits_per_sample=16, samples_signed=True)
audio = AudioOut(board.GP0)
audio.play(mixer)

i = 0

audio.play(mixer)

def wait(time):
    deadline = ticks_add(ticks_ms(), time)
    while ticks_less(ticks_ms(), deadline):
        pass
def play_sound(mixer_voice,ssound):
    mixer.voice[mixer_voice].play(ssound)
def set_led(index,vvalue):
    leds[index].value = vvalue

def play_sound_and_light(ss,i):
    mixer.voice[i].play(ss)
    leds[i].value = True
    deadline = ticks_add(ticks_ms(), bpm_millis)
    while ticks_less(ticks_ms(), deadline):
        pass
    leds[i].value = False


while True:
    set_led(0,True)
    play_sound(0,kick)
    play_sound(2,hihat)
    wait(bpm_millis)
    set_led(0,False)

    set_led(1,True)
    play_sound(2,hihat)
    wait(bpm_millis)
    set_led(1,False)



