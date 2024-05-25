import board
from ssd1306 import SSD1306_I2C
from time import sleep

id = 0
sda = board.Pin(0)
scl = board.Pin(1)

i2c = board.I2C(id=id, scl=board.scl, sda=board.sda)

oled = SSD1306_I2C(width=128, height=64, i2c=i2c)

oled.init_display()
oled.text("Test 1",1,1)
oled.show()
sleep(1)