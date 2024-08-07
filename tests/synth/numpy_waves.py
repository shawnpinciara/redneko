# https://dsp.stackexchange.com/questions/76394/python-fm-modulation
import numpy as np
import matplotlib.pyplot as plt


#see here for correct formula
# #https://gist.github.com/gamblor21/15a430929abf0e10eeaba8a45b01f5a8

#tod tips and tricks wave creation
# https://github.com/todbot/circuitpython-synthio-tricks?tab=readme-ov-file#making-your-own-waves

SAMPLE_SIZE=512
SAMPLE_VOLUME=5000
sin = np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False))
wave_sine = np.array(sin * SAMPLE_VOLUME, dtype=np.int16)
    
print(sin)
plt.plot(wave_sine)
plt.xlabel("Time(s)")
plt.ylabel("Amplitude")
plt.show()