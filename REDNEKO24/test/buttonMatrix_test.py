# SPDX-FileCopyrightText: 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import keypad # type: ignore
import board # type: ignore
import pins as p

km = keypad.KeyMatrix(
    row_pins=(p.row1_pin,),
    column_pins=(p.col1_pin,p.col2_pin,p.col3_pin),
)

while True:
    event = km.events.get()
    if event:
        print(event)
        print(event.pressed)
