# SPDX-FileCopyrightText: Copyright (c) 2024 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
:py:class:`~adafruit_hx711.hx711.HX711`
================================================================================

CircuitPython driver for the HX711 24-bit ADC for Load Cells / Strain Gauges


* Author(s): Liz Clark

Implementation Notes
--------------------

**Hardware:**

* `Link Text <https://www.adafruit.com/product/5974>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

import time

try:
    from typing import Union  # pylint: disable=unused-import
    import digitalio
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/your-repo/Adafruit_CircuitPython_HX711.git"


class HX711:
    """HX711 ADC driver"""

    CHAN_A_GAIN_128 = 25
    CHAN_A_GAIN_64 = 27
    CHAN_B_GAIN_32 = 26

    def __init__(
        self, data_pin: digitalio.DigitalInOut, clock_pin: digitalio.DigitalInOut
    ) -> None:
        """
        Initialize the HX711 module.

        :param data_pin: The data pin.
        :param clock_pin: The clock pin.
        """
        self._data_pin = data_pin
        self._clock_pin = clock_pin
        self._tare_value_a = 0
        self._tare_value_b = 0
        self._initialize()

    def _initialize(self) -> None:
        """Perform a power reset and wake up the HX711."""
        self.power_down(True)  # Perform a power reset
        time.sleep(0.001)  # Hold pin high for 1 ms for reset
        self.power_down(False)  # Wake up

    def power_down(self, down: bool) -> None:
        """
        Power down or wake up the HX711.

        :param down: True to power down, False to wake up.
        """
        self._clock_pin.value = down

    def read_channel_blocking(self, chan_gain: int) -> int:
        """
        Read ADC value with specified gain in a blocking manner.

        :param chan_gain: Gain and channel configuration.
        :return: ADC value.
        """
        self._read_channel(
            chan_gain
        )  # First, set the desired gain and discard this read
        return self._read_channel(chan_gain)  # Now perform the actual read

    def _read_channel(self, chan_gain: int) -> int:
        """
        Read ADC value with specified gain.

        :param chan_gain: Gain and channel configuration.
        :return: ADC value.
        """
        return self._read_channel_raw(chan_gain) - (
            self._tare_value_b
            if chan_gain == self.CHAN_B_GAIN_32
            else self._tare_value_a
        )

    def _read_channel_raw(self, chan_gain: int) -> int:
        """
        Read raw ADC value with specified gain.

        :param chan_gain: Gain and channel configuration.
        :return: Raw ADC value.
        """
        while self.is_busy:
            pass  # Wait until the HX711 is ready

        self._clock_pin.value = False
        value = 0
        for _ in range(24):  # Read 24 bits from DOUT
            self._clock_pin.value = True
            time.sleep(0.000001)  # 1 microsecond delay
            value = (value << 1) | self._data_pin.value
            self._clock_pin.value = False
            time.sleep(0.000001)  # 1 microsecond delay

        # Set gain for next reading
        for _ in range(chan_gain - 24):
            self._clock_pin.value = True
            self._clock_pin.value = False

        # Convert to 32-bit signed integer
        if value & 0x800000:
            value |= 0xFF000000

        return value

    @property
    def is_busy(self) -> bool:
        """
        Check if the HX711 is busy.

        :return: True if busy, False otherwise.
        """
        return self._data_pin.value

    @property
    def tare_value_a(self) -> int:
        """
        Get the tare value for channel A.

        :return: Tare value for channel A.
        """
        return self._tare_value_a

    @tare_value_a.setter
    def tare_value_a(self, tare_value: int) -> None:
        """
        Set the tare value for channel A.

        :param tare_value: Tare value for channel A.
        """
        self._tare_value_a = tare_value

    @property
    def tare_value_b(self) -> int:
        """
        Get the tare value for channel B.

        :return: Tare value for channel B.
        """
        return self._tare_value_b

    @tare_value_b.setter
    def tare_value_b(self, tare_value: int) -> None:
        """
        Set the tare value for channel B.

        :param tare_value: Tare value for channel B.
        """
        self._tare_value_b = tare_value

    def read(self, chan_gain: int = CHAN_A_GAIN_128) -> int:
        """
        Read ADC value with specified gain.

        :param chan_gain: Gain and channel configuration.
        :return: ADC value.
        """
        return self.read_channel_blocking(chan_gain)
