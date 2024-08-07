# SPDX-FileCopyrightText: 2022 Blitz City DIY
# SPDX-License-Identifier: MIT
# MIDI UART in/MIDI USB out

#https://github.com/BlitzCityDIY/midi_uart_experiments/blob/main/CircuitPython/1-23-22_midiUartIn_USB-out.py

import time
import board # type: ignore
import busio # type: ignore

#MIDI
import adafruit_midi # type: ignore
import usb_midi # type: ignore
from adafruit_midi.control_change import ControlChange # type: ignore
from adafruit_midi.note_off import NoteOff# type: ignore
from adafruit_midi.note_on import NoteOn# type: ignore

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

def midi_to_hz(note_number):
    #From: https://github.com/craffel/pretty-midi/blob/main/pretty_midi/utilities.py#L255
    # MIDI note numbers are defined as the number of semitones relative to C0
    # in a 440 Hz tuning
    return 440.0*(2.0**((note_number - 69)/12.0))

#BUZZER
import pwmio # type: ignore
buzzer = pwmio.PWMOut(board.GP2, variable_frequency=True)
a = 12
buzzer.duty_cycle = 2**a


#SYNTH
note_pres = 42
note_prev = 57
def noteOn(midi_note):
    global note_prev
    global note_pres
    note_prev = int(midi_to_hz(note_pres))
    note_pres = int(midi_to_hz(midi_note))
    
    print(str(note_prev) + " to " + str(note_pres))
    for slide in range(note_prev,note_pres):
        buzzer.frequency = slide
        time.sleep(.008)
        #buzzer.frequency = int(midi_to_hz(note))
    


while True:
    msg = midi.receive()
    if isinstance(msg,NoteOn):
        #midi.send(msg)
        # print(msg)
        buzzer.duty_cycle = 2**a
        noteOn(msg.note)
    elif isinstance(msg,NoteOff):
        #buzzer.duty_cycle = 2**5
        print("Off")