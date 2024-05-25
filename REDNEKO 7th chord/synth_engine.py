import synthio
import audiopwmio
import adafruit_wave
import ulab.numpy as np
import random
import time, board, digitalio, audiomixer, analogio, neopixel, asyncio
from audiocore import WaveFile


# SOUNDS:
wavetable_fname = "wav/REALIZE.WAV"  # from https://waveeditonline.com/
wavetable_sample_size = 256  # number of samples per wave in wavetable (256 is standard)
sample_rate = 25000
wave_lfo_min = 0  # which wavetable number to start from
wave_lfo_max = 10  # which wavetable number to go up to

# MIXER (OUTS)
audio = audiopwmio.PWMAudioOut(board.GP0)
mixer = audiomixer.Mixer(
    voice_count=4,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)
synth = synthio.Synthesizer(channel_count=1, sample_rate=22050)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 1



def lerp(a, b, t):  return (1-t)*a + t*b

class Wavetable:
    """ A 'waveform' for synthio.Note that uses a wavetable w/ a scannable wave position."""
    def __init__(self, filepath, wave_len=256):
        self.w = adafruit_wave.open(filepath)
        self.wave_len = wave_len  # how many samples in each wave
        if self.w.getsampwidth() != 2 or self.w.getnchannels() != 1:
            raise ValueError("unsupported WAV format")
        self.waveform = np.zeros(wave_len, dtype=np.int16)  # empty buffer we'll copy into
        self.num_waves = self.w.getnframes() // self.wave_len
        self.set_wave_pos(0)

    def set_wave_pos(self, pos):
        """Pick where in wavetable to be, morphing between waves"""
        pos = min(max(pos, 0), self.num_waves-1)  # constrain
        samp_pos = int(pos) * self.wave_len  # get sample position
        self.w.setpos(samp_pos)
        waveA = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        self.w.setpos(samp_pos + self.wave_len)  # one wave up
        waveB = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        pos_frac = pos - int(pos)  # fractional position between wave A & B
        self.waveform[:] = lerp(waveA, waveB, pos_frac) # mix waveforms A & B


wavetable1 = Wavetable(wavetable_fname, wave_len=wavetable_sample_size)
wavetable1.set_wave_pos(6)
amp_env = synthio.Envelope(sustain_level=0.8, attack_time=0.05, release_time=0.3)
wave_lfo = synthio.LFO(rate=0.1, waveform=np.array((0,32767), dtype=np.int16) )
lpf = synth.low_pass_filter(4000, 1)  # cut some of the annoying harmonics

synth.blocks.append(wave_lfo)  # attach wavelfo to global lfo runner since cannot attach to note



def truncate_float(float_number, decimal_places):
    multiplier = 10 ** decimal_places
    return int(float_number * multiplier) / multiplier


async def play_chord_async(delay,button,led,s_note,chord_arr):
    while True:
        await button.pressed()
        synth.release_all()
        #bass root

        f = synthio.midi_to_hz(s_note-36) # + random.uniform(-0.1,0.1) )
        vibrato_lfo = synthio.LFO(rate=1, scale=0.01)
        note = synthio.Note( frequency=f, waveform=wavetable1.waveform,envelope=amp_env, filter=lpf, bend=vibrato_lfo )
        synth.press(note)
        #7t chord
        for i in range(0,4):
            f = synthio.midi_to_hz(s_note+chord_arr[i]-(random.randint(0,1)*12)) # + random.uniform(-0.1,0.1) )
            note = synthio.Note( frequency=f, waveform=wavetable1.waveform,envelope=amp_env, filter=lpf, bend=vibrato_lfo )
            synth.press(note)
        led.value = True
        await button.released()
        led.value = False
    await asyncio.sleep(delay)

async def stop_play_async(delay,button):
    while True:
        await button.pressed()
        synth.release_all()
    await asyncio.sleep(delay)
