import board
import digitalio
import time


#buzzer GP2
#encoder: GP3,GP4 GP5(button)
#Button: GP29
#PCM5102:
# LCK - 28
# DIN - 27
# BCK - 26

    
# SPDX-FileCopyrightText: 2022 Blitz City DIY
# SPDX-License-Identifier: MIT
# MIDI UART in/MIDI USB out

#https://github.com/BlitzCityDIY/midi_uart_experiments/blob/main/CircuitPython/1-23-22_midiUartIn_USB-out.py

#MIDI IN
import adafruit_midi # type: ignore
import usb_midi # type: ignore
from adafruit_midi.control_change import ControlChange# type: ignore
from adafruit_midi.note_off import NoteOff# type: ignore
from adafruit_midi.note_on import NoteOn# type: ignore
import busio # type: ignore


#                       TX         RX
uart = busio.UART(board.GP0, board.GP1, baudrate=31250, timeout=0.001)
midi_in_channel = 1
midi_out_channel = 2
midi = adafruit_midi.MIDI(
    midi_in=uart,
    midi_out=usb_midi.ports[1],
    out_channel=(midi_out_channel - 1),
    debug=False,
)

def mapp(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

#SYNTHESIS
import audiobusio
i2s_bclk = board.GP26  # BIT BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)
i2s_wsel = board.GP27 # WORD SELECT LCK on PCM5102
i2s_data = board.GP28 # DIN on PCM5102
audio = audiobusio. I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)
import synthio
import audiomixer


import ulab.numpy as np
SAMPLE_SIZE = 512
SAMPLE_VOLUME = 32000  # 0-32767
wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16)
mixer = audiomixer.Mixer(channel_count=1, sample_rate=22050, buffer_size=2048)
env = synthio.Envelope(attack_time=0.05,release_time=0.05)
lfo = synthio.LFO(rate=0, scale=0.05)
synth = synthio.Synthesizer(channel_count=1, sample_rate=22050, envelope=env)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 1

#GLIDE
glide_time = 0.06
def glide(note_start:int,note_end:int):
    global wave_sine,lfo,glide_time
    glide_steps = 50
    glide_deltat = glide_time / glide_steps
    f = synthio.midi_to_hz(note_start)
    note = synthio.Note(frequency=f,waveform = wave_sine,bend=lfo)
    #note one
    synth.release_all_then_press(note)
    for i in range(glide_steps):
        slid_note = note_start + i*((note_end - note_start)/glide_steps)
        note.frequency = synthio.midi_to_hz(slid_note)
        time.sleep(glide_deltat)


#MAIN

#https://github.com/todbot/circuitpython-synthio-tricks?tab=readme-ov-file#advanced-techniques

notes_pressed = []  # which notes being pressed. key=midi note, val=note object
pressed_i = -1 

import thisbutton as tb
# https://github.com/elliotmade/This-Button

btn = tb.thisButton(board.GP29, True)
def btnPushed():
    global lfo
    print("Boop")
    lfo = synthio.LFO(rate=5, scale=0.05)
btn.assignClick(btnPushed)

import rotaryio
encoder_1 = board.GP3
encoder_2 = board.GP4
encoder_sw = tb.thisButton(board.GP5,True)
encoder = rotaryio.IncrementalEncoder(encoder_2, encoder_1)
last_position = None
def encoderRotated(direction,pos):
    global glide_time
    glide_time = mapp(pos,0,10,0.05,0.5)
    if glide_time < 0.05: glide_time=0.05
    if glide_time >0.5: glide_time=0.5
    print(glide_time)

def encoderPushed():
    print("encoder pressed")
encoder_sw.assignClick(encoderPushed)

while True:
    # buttons
    btn.tick()
    encoder_sw.tick()

    # encoder
    position = encoder.position
    if position != last_position and last_position is not None:
        encoderRotated(position-last_position,position)
    last_position = position

    # midi
    msg = midi.receive()
    if isinstance(msg, NoteOn) and msg.velocity != 0:  # NoteOn
        notes_pressed.append(msg.note)
        pressed_i+=1
        if pressed_i==0:
            glide(notes_pressed[0],notes_pressed[0])
        else:
            glide(notes_pressed[pressed_i-1],notes_pressed[pressed_i])
        if len(notes_pressed)==1:
            print("attack")
    elif isinstance(msg,NoteOff) or isinstance(msg,NoteOn) and msg.velocity==0:  # NoteOff
        pressed_i-=1
        if notes_pressed.index(msg.note) == len(notes_pressed)-1 and len(notes_pressed)>=2:
            glide(notes_pressed[-1],notes_pressed[-2])
        notes_pressed.pop(notes_pressed.index(msg.note))
        if len(notes_pressed) == 0:
            synth.release_all()
         
        
            



        
        