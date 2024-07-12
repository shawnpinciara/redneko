
# SPDX-FileCopyrightText: 2024 Shawn Pinciara (@shawnpinciara)
# SPDX-License-Identifier: MIT

import time
import board 

import audiomixer
import synthio 


# for PWM audio 
# import audiopwmio 
# audio = audiopwmio.PWMAudioOut(board.GP1)

# DAC
import audiobusio
i2s_bclk = board.GP26  # BIT BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)
i2s_wsel = board.GP27 # WORD SELECT LCK on PCM5102
i2s_data = board.GP28 # DIN on PCM5102

audio = audiobusio. I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)
mixer = audiomixer.Mixer(channel_count=1, sample_rate=22050, buffer_size=2048)
synth = synthio.Synthesizer(channel_count=1, sample_rate=22050)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 1


def glide(note_start,note_end):
    glide_time = 3
    glide_steps = 100
    glide_deltat = glide_time / glide_steps
    f = synthio.midi_to_hz(note_start)
    note = synthio.Note(frequency=f)
    synth.release_all_then_press(note) #for monophonic synth
    for i in range(glide_steps):
        slid_note = note_start + i*((note_end - note_start)/glide_steps)
        note.frequency = synthio.midi_to_hz(slid_note)
        time.sleep(glide_deltat)

glide(70,30)
glide(30,40)
glide(40,10)


