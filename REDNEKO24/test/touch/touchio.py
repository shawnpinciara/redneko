import board # type: ignore
import touchio
from adafruit_debouncer import Debouncer, Button # type: ignore

#From here:
#https://diyelectromusic.com/2023/06/12/raspberry-pi-pico-capacitive-touch/

THRESHOLD = 1000
t = touchio.TouchIn(board.GP21)
t.threshold = t.raw_value + THRESHOLD
touchpad = Button(t, value_when_pressed=True)

while True:
    touchpad.update()
    if touchpad.rose:
        print("Touch On")
    if touchpad.fell:
        print("Touch Off")
