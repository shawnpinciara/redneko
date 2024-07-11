
# SPDX-FileCopyrightText: 2022 Blitz City DIY
# SPDX-License-Identifier: MIT
# MIDI UART in/MIDI USB out

#https://github.com/BlitzCityDIY/midi_uart_experiments/blob/main/CircuitPython/1-23-22_midiUartIn_USB-out.py

import time
import board # type: ignore





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

#SYNTHESIS
import audiobusio
i2s_bclk = board.GP26  # BIT BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)
i2s_wsel = board.GP27 # WORD SELECT LCK on PCM5102
i2s_data = board.GP28 # DIN on PCM5102
audio = audiobusio. I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)
import synthio
import audiomixer


mixer = audiomixer.Mixer(channel_count=1, sample_rate=22050, buffer_size=2048)
env = synthio.Envelope(attack_time=0.05,release_time=0.05)
synth = synthio.Synthesizer(channel_count=1, sample_rate=22050, envelope=env)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 1
SAMPLE_SIZE = 512
SAMPLE_VOLUME = 5000
import ulab.numpy as np
wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16)
#GLIDE
def glide(note_start,note_end):
    global wave_sine
    glide_time = 0.06
    glide_steps = 50
    glide_deltat = glide_time / glide_steps
    f = synthio.midi_to_hz(note_start)
    note = synthio.Note(frequency=f,waveform = wave_sine)
    #note one
    synth.release_all_then_press(note)
    for i in range(glide_steps):
        slid_note = note_start + i*((note_end * note_start)/glide_steps)
        print(slid_note)
        note.frequency = synthio.midi_to_hz(slid_note)
        time.sleep(glide_deltat)


#MAIN
pres = 60
past = 60
first_time = True

#https://github.com/todbot/circuitpython-synthio-tricks?tab=readme-ov-file#advanced-techniques

notes_pressed = []  # which notes being pressed. key=midi note, val=note object
while True:
    msg = midi.receive()
    if isinstance(msg, NoteOn) and msg.velocity != 0:  # NoteOn
        notes_pressed.append(msg.note)
        past = pres
        pres = msg.note
        if first_time:
            first_time = False
            past = msg.note
        print(str(past) + " "+ str(pres))
        glide(past,pres)
    elif isinstance(msg,NoteOff) or isinstance(msg,NoteOn) and msg.velocity==0:  # NoteOff
        try:
            notes_pressed.pop(notes_pressed.index(msg.note))
            synth.release(msg.note)
        except:
            pass
        if len(notes_pressed) != 0:
            print(notes_pressed) #last element
            #synth press last

# mixer.voice[0].level = 1
        
        