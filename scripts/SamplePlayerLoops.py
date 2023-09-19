# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials Audio Out WAV example"""
import time, board,digitalio,audiomixer,analogio
from audiocore import WaveFile
from adafruit_ticks import ticks_ms, ticks_add, ticks_less, ticks_diff


try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!
#VARIABLES
bpm = 300
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
btn3 = digitalio.DigitalInOut(board.GP13)
btn3.switch_to_input(pull=digitalio.Pull.UP)
led3 = digitalio.DigitalInOut(board.GP12)
led3.direction = digitalio.Direction.OUTPUT
btn4 = digitalio.DigitalInOut(board.GP11)
btn4.switch_to_input(pull=digitalio.Pull.UP)
led4 = digitalio.DigitalInOut(board.GP10)
led4.direction = digitalio.Direction.OUTPUT
pot1 = analogio.AnalogIn(board.GP28_A2) #to read it: pot1.value 0 to 65535
#pot2 = analogio.AnalogIn(board.GP26_A0)

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

#PROGRAM VARIABLES
sequence1 = [1,0,0,0] #kick
sequence2 = [0,0,1,0] #snare
sequence3 = [1,1,0,1] #hihat
mode = 0 #0=play,1=sound,2=sequence,3=layer
play = True
btn1_debounce = True
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

def mapp(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)
j = 0
while True:
    if (j>3):
        j=0
    set_led(j,True)
    if play==True:
        if (sequence1[j]==1):
            play_sound(0,kick)
        if (sequence2[j]==1):
            play_sound(2,snare)
        if (sequence3[j]==1):
            play_sound(2,hihat)
    start_timer = ticks_ms() #start timer
    #DO STUFF HERE
    #bisogna sperare che il codice qua in mezzo esegua in meno tempo di un battito
    pot1_value = mapp(pot1.value,65535,0,0,65535)
    bpm = mapp(pot1_value,0,65535,40,300)
    if pot1_value < 13107:
        mode = 0 #play
    elif pot1_value < 26214:
        mode = 1 #sound
    elif pot1_value < 39321:
        mode = 2 #pattern
    elif pot1_value < 52428:
        mode = 3
    else:
        mode = 4

    if btn1.value == False and btn1_debounce==True:
        btn1_debounce = False
        #check mode and answer correctly
        print(pot1_value)

        if mode == 0:
            play = not play
        if mode == 1:
            sequence1[0] = not sequence1[0]
    if btn1.value == True:
        btn1_debounce = True

    #
    #FINISH TO DO STUFF HERE
    wait(bpm_millis)
    set_led(j,False)
    j+=1
    start_timer = 0
