import time, board, audiocore, audiomixer
from audiopwmio import PWMAudioOut as AudioOut

wav_files = ("/loops/1/loop1.wav", "/loops/1/loop2.wav", "/loops/1/loop3.wav","/loops/1/loop4.wav")
wavs = [None] * len(wav_files)  # holds the loaded WAVs

audio = AudioOut(board.GP15)  # RP2040 example
mixer = audiomixer.Mixer(voice_count=len(wav_files), sample_rate=22050, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer)  # attach mixer to audio playback

for i in range(len(wav_files)):
    print("i:",i)
    wavs[i] = audiocore.WaveFile(open(wav_files[i], "rb"))
    mixer.voice[i].play( wavs[i], loop=True) # start each one playing

while True:
    #print("doing something else while all loops play")
    time.sleep(5)# Write your code here :-)
