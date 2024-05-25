# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import rotaryio # type: ignore
import board # type: ignore
import pins as p

encoder = rotaryio.IncrementalEncoder(p.encoder_1, p.encoder_2)
last_position = None
while True:
    position = encoder.position
    if last_position is None or position != last_position:
        print(position)
    last_position = position
