
# SPDX-FileCopyrightText: 2023 John Park and @todbot / Tod Kurt
#
# SPDX-License-Identifier: MIT

import time
import board
import digitalio
import audiomixer
import synthio

# for PWM audio with an RC filter
import audiopwmio
audio = audiopwmio.PWMAudioOut(board.GP0)

mixer = audiomixer.Mixer(channel_count=1, sample_rate=22050, buffer_size=2048)
amp_env_slow = synthio.Envelope(
                                attack_time=0.2,
                                sustain_level=1.0,
                                release_time=0.8
)

synth = synthio.Synthesizer(channel_count=1, sample_rate=22050,envelope=amp_env_slow)
synth.envelope = amp_env_slow

audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 1

while True:
    synth.press((65, 69, 72))  # midi note 65 = F4
    time.sleep(0.5)
    synth.release((65, 69, 72))  # release the note we pressed
    time.sleep(0.5)
    #mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4  # reduce volume each pass
