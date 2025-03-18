##################################################################################
## MIT License
##
## Copyright (c) 2019-2020 Vicon Motion Systems Ltd
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##################################################################################
"""Module containing Vicon time measurement helper."""

from datetime import timedelta
from functools import total_ordering
from numbers import Integral

from vicon_core_api import SchemaServices


# This is the reference clock rate for Vicon systems.
TICK_RATE_135MHZ = 135000000

# The tick type is a 64-bit integer, which is specified as a long in Python 2.
try:
    TICK_TYPE = long
except NameError:
    TICK_TYPE = int


@total_ordering
class ViconTick135MHz(object):
    """Representation of a time difference, measured in ticks of a notional reference clock running at 135MHz.

    Members:
        tick < numbers.Integral >: Number of clock ticks.
    """
    def __init__(self, tick=0):
        """Initialiser for ViconTick135MHz."""
        if isinstance(tick, Integral):
            self.tick = tick
        elif isinstance(tick, ViconTick135MHz):
            self.tick = tick.tick
        else:
            raise TypeError("Type of tick is not integer or ViconTick135MHz: %s" % type(tick))

    def __repr__(self):
        """Provide JSON string representation for ViconTick135MHz."""
        return SchemaServices.write(self)

    def __str__(self):
        """Provide JSON string representation for ViconTick135MHz."""
        return SchemaServices.write(self)

    def __eq__(self, other):
        if not isinstance(other, ViconTick135MHz):
            return NotImplemented
        return self.tick == other.tick

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if not isinstance(other, ViconTick135MHz):
            return NotImplemented
        return self.tick < other.tick

    def __add__(self, other):
        if not isinstance(other, ViconTick135MHz):
            return NotImplemented
        return ViconTick135MHz(self.tick + other.tick)

    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        if not isinstance(other, ViconTick135MHz):
            return NotImplemented
        self.tick += other.tick
        return self

    def __sub__(self, other):
        if not isinstance(other, ViconTick135MHz):
            return NotImplemented
        return ViconTick135MHz(self.tick - other.tick)

    def __rsub__(self, other):
        return self - other

    def __isub__(self, other):
        if not isinstance(other, ViconTick135MHz):
            return NotImplemented
        self.tick -= other.tick
        return self

    def __mul__(self, tick):
        if isinstance(tick, Integral):
            return ViconTick135MHz(self.tick * tick)
        if isinstance(tick, ViconTick135MHz):
            return ViconTick135MHz(self.tick * tick.tick)
        return NotImplemented

    def __rmul__(self, tick):
        return self * tick

    def __imul__(self, tick):
        if isinstance(tick, Integral):
            self.tick *= tick
            return self
        if isinstance(tick, ViconTick135MHz):
            self.tick *= tick.tick
            return self
        return NotImplemented

    def seconds(self):
        """Get tick value in seconds."""
        return self.tick / float(TICK_RATE_135MHZ)

    def timedelta(self):
        """Return approximation of tick value as a datetime.timedelta (rounded to the nearest microsecond)."""
        return timedelta(seconds=self.seconds())

    def sample_number(self, sample_period_in_ticks):
        """Return the number of samples relative to tick 0, given the sample period in ticks. The tick value will be rounded towards zero."""
        if not isinstance(sample_period_in_ticks, Integral):
            raise TypeError("sample_period_in_ticks is not an integer: %s" % type(sample_period_in_ticks))
        return self.tick / sample_period_in_ticks

    @staticmethod
    def from_timedelta(time_delta):
        """Create ViconTick135MHz from a datetime.timedelta value. The tick value will be rounded away from zero."""
        ticks_float = round(time_delta.total_seconds() * TICK_RATE_135MHZ)
        return ViconTick135MHz(TICK_TYPE(ticks_float))


SchemaServices.register_json_schema(ViconTick135MHz, """{"Type": "NamedTuple", "TypeName": "ViconTick135MHz", "SubSchemas": [["Tick", {"Type": "Int64"}]]}""")
