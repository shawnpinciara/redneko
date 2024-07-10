# https://dsp.stackexchange.com/questions/76394/python-fm-modulation
import numpy as np
import matplotlib.pyplot as plt

SAMPLE_SIZE=512
SAMPLE_VOLUME=5000
sin = np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False))
wave_sine = np.array(sin * SAMPLE_VOLUME, dtype=np.int16)
    
print(sin)
plt.plot(wave_sine)
plt.xlabel("Time(s)")
plt.ylabel("Amplitude")
plt.show()