import board # type: ignore


import touchio
from adafruit_debouncer import Debouncer, Button # type: ignore

import time

#From here:
#https://diyelectromusic.com/2023/06/12/raspberry-pi-pico-capacitive-touch/

t = touchio.TouchIn(board.GP18)

while True:
    print(t.raw_value)
    time.sleep(0.1)
