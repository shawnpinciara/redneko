
# SPDX-FileCopyrightText: 2023 John Park and @todbot / Tod Kurt
#
# SPDX-License-Identifier: MIT

import time
import board # type: ignore

import audiomixer # type: ignore
import synthio # type: ignore


# for PWM audio with an RC filter
# import audiopwmio # type: ignore
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

while True:
    synth.release_all_then_press((65, 69, 72))  # midi note 65 = F4
    print("note")
    time.sleep(0.5)
    synth.release_all_then_press((65, 69+12, 72))  # release the note we pressed
    time.sleep(0.5)
    #mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4  # reduce volume each pass
