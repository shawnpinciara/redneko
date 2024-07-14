import board # type: ignore
import neopixel
import time

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False) # type: ignore


def light(color):
    pixels[0] = color
    pixels.show() # type: ignore

sleep = 0.01

def slide():
    global sleep
    for r in range(0,255):
        pixels[0] = (r, 0, 0)
        pixels.show() # type: ignore
        time.sleep(sleep)
    for g in range(0,255):
        pixels[0] = (255, g, 0)
        pixels.show() # type: ignore
        time.sleep(sleep)
    for a in range(255,0,-1):
        pixels[0] = (a, a, 0)
        pixels.show() # type: ignore
        time.sleep(sleep)

ambulance_sleep = 0.1
def ambulance():
    pixels[0] = (255, 0, 0)
    pixels.show() # type: ignore
    time.sleep(ambulance_sleep)
    pixels[0] = (0, 0, 255)
    pixels.show() # type: ignore
    time.sleep(ambulance_sleep)

while True:
    slide()
    # ambulance()
    


