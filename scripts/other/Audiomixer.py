import board
import audiocore
import audiomixer
import digitalio
import time
from audiopwmio import PWMAudioOut as AudioOut

a = AudioOut(board.GP15)
music = audiocore.WaveFile(open("/loops/1/loop.wav", "rb"))
drum = audiocore.WaveFile(open("/loops/1/loop1.wav", "rb"))
mixer = audiomixer.Mixer(voice_count=2, sample_rate=22050, channel_count=1,bits_per_sample=16, samples_signed=True)

print("playing")
# Have AudioOut play our Mixer source
a.play(mixer)
# Play the first sample voice
mixer.voice[0].play(music)
while mixer.playing:
  #mixer.voice[1].play(drum)
  #time.sleep(1)
  pass
mixer.voice[0].play(music)
print("stopped")
