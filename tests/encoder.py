# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import rotaryio # type: ignore
import board # type: ignore


encoder_1 = board.GP3
encoder_2 = board.GP4
encoder_sw = board.GP5

encoder = rotaryio.IncrementalEncoder(encoder_2, encoder_1)
last_position = None
while True:
    position = encoder.position
    if last_position is None or position != last_position:
        print(position)
    last_position = position
