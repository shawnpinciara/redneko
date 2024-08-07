# SPDX-FileCopyrightText: 2022 Blitz City DIY
# SPDX-License-Identifier: MIT
# MIDI UART in/MIDI USB out

#https://github.com/BlitzCityDIY/midi_uart_experiments/blob/main/CircuitPython/1-23-22_midiUartIn_USB-out.py

import time
import board 


import busio 
import adafruit_midi 
import usb_midi 
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.midi_message import MIDIUnknownEvent
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

print("MIDI UART In/USB Out")
print("Default output channel:", midi.out_channel + 1)

while True:
    msg = midi.receive()
    if msg != None:
        print(msg)
    if isinstance(msg,NoteOn):
        #midi.send(msg)
        print(msg)
        print(msg.note)
    elif isinstance(msg,NoteOff):
        #buzzer.duty_cycle = 2**5
        print("Off")
    elif isinstance(msg,ControlChange):
        print(msg.value)
    elif isinstance(msg,MIDIUnknownEvent):
        print(msg.status)