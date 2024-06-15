# https://mastodon.social/@todbot/112610331112413354 HOW TO IMPLEMENT BEND
# https://docs.circuitpython.org/en/latest/shared-bindings/synthio/index.html#synthio.Note.bend BEND OPTION

import time
import board # type: ignore
import digitalio # type: ignore
import audiomixer # type: ignore
import synthio # type: ignore

# for PWM audio with an RC filter
import audiopwmio # type: ignore
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

f = synthio.midi_to_hz(52)
note = synthio.Note(frequency=f)

synth.press(note)
note.bend(float(0))
# for i in range(1,12):
#     note.bend(1/12)

# while True:
#     synth.press((65, 69, 72))  # midi note 65 = F4
#     time.sleep(0.5)
#     synth.release((65, 69+11, 72))  # release the note we pressed
#     time.sleep(0.5)
#     #mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4  # reduce volume each pass
