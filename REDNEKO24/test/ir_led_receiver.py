import board
import digitalio
import analogio
import time

# https://electronics.stackexchange.com/questions/160720/arduino-ir-receiver

led = digitalio.DigitalInOut(board.GP22)
led.direction = digitalio.Direction.OUTPUT

ir_receiver = analogio.AnalogIn(board.A2)

while True:
    led.value = 0
    print(ir_receiver.value)
    time.sleep(.5)
    
    led.value = 0
    print(ir_receiver.value)
    time.sleep(.5)