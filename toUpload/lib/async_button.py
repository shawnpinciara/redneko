# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Phil Underwood for Underwood Underground
#
# SPDX-License-Identifier: MIT
"""
`async_button`
================================================================================

a library for reading buttons using asyncio


* Author(s): Phil Underwood

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* CircuitPython asyncio module:
  https://github.com/adafruit/Adafruit_CircuitPython_asyncio

* CircuitPython ticks module:
  https://github.com/adafruit/Adafruit_CircuitPython_Ticks
"""


__version__ = "1.2.3"
__repo__ = "https://github.com/furbrain/CircuitPython_async_button.git"

import asyncio
from asyncio import Event

from adafruit_ticks import ticks_add, ticks_less, ticks_ms

try:
    from typing import Dict, Sequence, Awaitable, Any, Union
except ImportError:
    pass

import digitalio
import keypad
from microcontroller import Pin
import countio


class SimpleButton:
    """
    Asynchronous interface to a button or other IO input. This does not create a background
    task.
    """

    def __init__(
        self, pin: Pin, value_when_pressed: bool, *, pull: bool = True, interval=0.05
    ):
        """

        :param Pin pin: Pin to wait for
        :param bool value_when_pressed: ``True`` if the pin reads high when the key is pressed.
          ``False`` if the pin reads low (is grounded) when the key is pressed.
        :param bool pull: ``True`` if an internal pull-up or pull-down should be enabled on the
          pin. A pull-up will be used if value_when_pressed is False; a pull-down will be used if
          it is ``True``. If an external pull is already provided for the pin, you can set
          pull to ``False``. However, enabling an internal pull when an external one is already
          present is not a problem; it simply uses slightly more current.
        :param float interval: How long to wait between checks of whether the button has changed.
          Default is 0.05s (human experience of "instantaneous" is up to 0.1s). This parameter
          can be set to zero and the button will be checked as often as possible, although other
          coroutines will still be able to run.
        """
        self.pin: Pin = pin
        self.value_when_pressed = value_when_pressed
        self.interval = interval
        if pull:
            self.pull = digitalio.Pull.DOWN if value_when_pressed else digitalio.Pull.UP
        else:
            self.pull = None

    async def pressed(self):
        """
        Wait until button is pressed
        """
        edge = countio.Edge.RISE if self.value_when_pressed else countio.Edge.FALL
        with countio.Counter(self.pin, edge=edge, pull=self.pull) as counter:
            while True:
                if counter.count > 0:
                    return
                await asyncio.sleep(self.interval)

    async def released(self):
        """
        Wait until button is released
        """
        edge = countio.Edge.FALL if self.value_when_pressed else countio.Edge.RISE
        with countio.Counter(self.pin, edge=edge, pull=self.pull) as counter:
            while True:
                if counter.count > 0:
                    return
                await asyncio.sleep(self.interval)


class TaskWrapper:
    """
    Create a task to run coro, then trigger event when finished
    Shouldn't really need this but CircuitPython does not have asyncio.wait or Task.result()
    """

    def __init__(self, coro: Awaitable, event: Event):
        """
        :param Awaitable coro: coroutine to run
        :param asyncio.Event event:
        """
        self._result = None
        self.coro = coro
        self.event = event
        self.task = asyncio.create_task(self._wait())

    async def _wait(self):
        self._result = await self.coro
        self.event.set()

    def done(self):
        """
        Check whether task has completed

        :return: True if task has completed
        """
        return self.task.done()

    def result(self):
        """
        Get return value from task

        :return: Whatever the task returned.
        """
        if not self.done():
            raise AssertionError("Task has not yet completed")
        return self._result

    def cancel(self):
        """
        Cancel the task
        :return:
        """
        self.task.cancel()


class Button:
    """
    This object will monitor the specified pin for changes and will report
    single, double, triple and long_clicks. It creates a background `asyncio` process
    that will monitor the button. The `events` chapter in the documentation shows when the
    various events are triggered
    """

    PRESSED = 1  #: Button has been pressed
    RELEASED = 2  #: Button has been released
    SINGLE = 4  #: Single click
    DOUBLE = 8  #: Double click
    TRIPLE = 16  #: Triple click
    LONG = 32  #: Long click
    ANY_CLICK = (
        SINGLE,
        DOUBLE,
        TRIPLE,
        LONG,
    )  #: Any of `SINGLE`, `DOUBLE`, `TRIPLE` or `LONG`
    ALL_EVENTS = (PRESSED, RELEASED, SINGLE, DOUBLE, TRIPLE, LONG)  #: Any event

    def __init__(
        self,
        pin: Pin,
        value_when_pressed: bool,
        *,
        pull: bool = True,
        interval: float = 0.020,
        double_click_max_duration=0.5,
        long_click_min_duration=2.0,
        double_click_enable: bool = True,
        triple_click_enable: bool = False,
        long_click_enable: bool = False,
    ):
        """
        Create the button object and start the background async process, this object must be
        created only when the asyncio event loop is running

        :param Pin pin: the pin to be monitored
        :param bool value_when_pressed: ``True`` if the pin reads high when the key is pressed.
          ``False`` if the pin reads low (is grounded) when the key is pressed.
        :param bool pull: ``True`` if an internal pull-up or pull-down should be enabled on
          the pin. A pull-up will be used if ``value_when_pressed`` is ``False``; a pull-down
          will be used if it is True. If an external pull is already provided for the pins,
          you can set pull to ``False``. However, enabling an internal pull when an external one
          is already present is not a problem; it simply uses slightly more current. Default is
          True.
        :param float interval: How long we wait between checking the state of the button. Default is
          0.02 (20 milliseconds), which is a good value for debouncing.
        :param float double_click_max_duration: how long in seconds before a second click is
          registered as a double click (this is also the value used for triple clicks.
          Default is 0.5 seconds.
        :param float long_click_min_duration: how long in seconds the button must be pressed before
          a long_click is triggered. Default is 2 seconds.
        :param bool double_click_enable: Whether double clicks are detected. Default is True.
        :param bool triple_click_enable: Whether triple clicks are detected. Default is False.
        :param bool long_click_enable: Whether long clicks are detected. Default is False.
        """
        self.pin = pin
        self.value_when_pressed = value_when_pressed
        #: Maximum separation between two clicks to register as double in seconds (default is 0.5s)
        self.double_click_max_duration = double_click_max_duration
        #: Minimum duration for a click to register as a long click in seconds. Default is 2s
        self.long_click_min_duration = long_click_min_duration
        self.interval = interval
        if not double_click_enable and triple_click_enable:
            raise ValueError("Must have double click enabled to use triple click")
        self.click_enabled = {
            self.DOUBLE: double_click_enable,
            self.TRIPLE: triple_click_enable,
            self.LONG: long_click_enable,
        }
        self.keys = keypad.Keys(
            (self.pin,),
            value_when_pressed=self.value_when_pressed,
            pull=pull,
            interval=self.interval,
        )
        self.monitor_task = asyncio.create_task(self._monitor())
        self.events = {
            x: asyncio.Event()
            for x in (
                self.SINGLE,
                self.DOUBLE,
                self.TRIPLE,
                self.LONG,
                self.PRESSED,
                self.RELEASED,
            )
        }
        self.last_click = self.SINGLE
        self.pressed = False

    async def _monitor(self):
        """
        This is the main background task that monitors key presses and releases
        """
        evt = keypad.Event(0, False)
        now = ticks_ms()
        long_click_due = ticks_add(now, int(self.long_click_min_duration * 1000))
        dbl_clk_expires = ticks_add(now, -100)
        while True:
            if self.keys.events.get_into(evt):
                if evt.pressed:
                    self._trigger(self.PRESSED)
                    now = getattr(
                        evt, "timestamp", ticks_ms()
                    )  # use now if timestamp not there
                    if ticks_less(now, dbl_clk_expires):
                        self._increase_clicks()
                    else:
                        self.last_click = self.SINGLE
                    long_click_due = ticks_add(
                        now, int(self.long_click_min_duration * 1000)
                    )
                    dbl_clk_expires = ticks_add(
                        now, int(self.double_click_max_duration * 1000)
                    )
                    self.pressed = True
                else:
                    self._trigger(self.RELEASED)
                    if self.last_click != self.LONG:
                        self._trigger(self.last_click)
                    else:
                        self.last_click = self.SINGLE
                    self.pressed = False
            else:
                if self.pressed and self.click_enabled[self.LONG]:
                    if (
                        ticks_less(long_click_due, ticks_ms())
                        and self.last_click != self.LONG
                    ):
                        self.last_click = self.LONG
                        self._trigger(self.LONG)
            await asyncio.sleep(self.interval)

    def _increase_clicks(self):
        if self.last_click == self.SINGLE and self.click_enabled[self.DOUBLE]:
            self.last_click = self.DOUBLE
        elif self.last_click == self.DOUBLE and self.click_enabled[self.TRIPLE]:
            self.last_click = self.TRIPLE
        else:
            self.last_click = self.SINGLE

    def _trigger(self, event: int):
        evt = self.events[event]
        evt.set()
        evt.clear()

    async def wait(self, click_types: Union[int, Sequence[int]] = ALL_EVENTS):
        """
        Wait for the first of the specified events.

        :param (List[int] | int) click_types: List of events to listen for. You can also pass a
          single event type in. Default is to listen for all events.
        :return: A list of the clicks that actually happened.

        :example:
          .. code-block:: python

            >>> async def get_click():
            >>>     # wait for a double or triple click
            >>>     clicks = await button.wait((Button.DOUBLE, Button.TRIPLE))
            >>>     if Button.DOUBLE in clicks:
            >>>         # do something

        """
        if isinstance(click_types, int):
            click_types = [click_types]
        # shortcut for efficiency: if only one click type awaited, just await that
        if len(click_types) == 1:
            await self.events[click_types[0]].wait()
            return [click_types[0]]

        # multiple click types - needs more complex algorithm
        evts: Dict[int, TaskWrapper] = {}
        one_event_done = asyncio.Event()
        for evt_type in click_types:
            coro = self.events[evt_type].wait()
            evts[evt_type] = TaskWrapper(coro, one_event_done)
        try:
            await one_event_done.wait()
            if len(evts) > 1:
                await asyncio.sleep(
                    0
                )  # ensure all event types get an opportunity to run
            results = []
            for evt_type, evt in evts.items():
                if evt.done():
                    results.append(evt_type)
            return results
        finally:
            # make sure all tasks are cancelled on exit
            for evt in evts.values():
                if not evt.done():
                    evt.cancel()

    async def wait_for_click(self):
        """
        Wait for any click and return it

        :return: Which click happened i.e. one of `SINGLE`, `DOUBLE`, `TRIPLE` or `LONG`
        """
        clicks = await self.wait(self.ANY_CLICK)
        return clicks[0]

    def deinit(self):
        """
        Deinitialise object and stop the background task
        """
        try:
            self.monitor_task.cancel()
        except KeyError:
            # sometimes get a key error if deinited before asyncio starts
            pass
        self.keys.deinit()


class MultiButton:
    """
    This class allows you to await the first click from any of two or more buttons
    """

    def __init__(self, **kwargs):
        """

        :param kwargs: pass each button that you want to be able to listen to with its name

        :example:
          .. code-block:: python

            >>> multi = MultiButton(a = button_a, b=button_b)
            >>> button, result = await multi.wait(a=Button.SINGLE, b= (Button.DOUBLE, Button.LONG))
            >>> # Long click on button B
            >>> print(button, result) # "b", Button.Long
        """
        for button in kwargs.values():
            if not isinstance(button, Button):
                raise TypeError("Must pass in async_button.Button as parameters")
        self.buttons: Dict[Any, Button] = kwargs

    async def wait(self, **kwargs):
        """
        Wait for any specified clicks

        :param kwargs: pass by keyword what clicks you want to listen for
        :return: button, click type
        :example:
          .. code-block:: python

            >>> multi = MultiButton(a = button_a, b=button_b)
            >>> button, result = await multi.wait(a=Button.SINGLE, b= (Button.DOUBLE, Button.LONG))
            >>> # Long click on button B
            >>> print(button, result) # "b", Button.Long
        """
        if len(kwargs) == 1:
            button = list(kwargs)[0]
            results = await self.buttons[button].wait(kwargs[button])
            return button, results[0]
        tasks: Dict[Any, TaskWrapper] = {}
        click_happened = asyncio.Event()
        for key, value in kwargs.items():
            tasks[key] = TaskWrapper(self.buttons[key].wait(value), click_happened)
        try:
            await click_happened.wait()
            result = (None, None)
            for key, task in tasks.items():
                if task.done():
                    result = (key, task.result()[0])
            return result
        finally:
            # make sure all tasks are cancelled on exit
            for task in tasks.values():
                if not task.done():
                    task.cancel()
