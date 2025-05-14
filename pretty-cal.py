import operator as op
import calendar as cal
import itertools as it
import functools as ft
from typing import ClassVar
from datetime import datetime
from argparse import ArgumentParser
from dataclasses import dataclass

@dataclass
class Month:
    month: int
    year: int
    _months: ClassVar[int] = 12

    def __add__(self, months):
        month = self.month + months
        if month > self._months:
            month %= self._months
            year = self.year + 1
        else:
            year = self.year

        return type(self)(month, year)

    @classmethod
    def from_datetime(cls, dt):
        return cls(dt.month, dt.year)

@dataclass
class Week:
    days: list
    month: Month
    start: bool = False

    def __post_init__(self):
        try:
            index = self.days.index(1)
        except ValueError:
            index = None
        self.start = index is not None

def cycle(month, n):
    for _ in range(n):
        yield from cal.monthcalendar(month.year, month.month)
        month += 1

def weeks(months):
    window = []
    for (i, m) in enumerate(months):
        if not i or all(m):
            yield Week(m)
        elif window:
            n = window.pop()
            days = list(it.starmap(op.add, zip(n, m)))
            yield Week(days)
        else:
            window.append(m)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--months', type=int)
    args = arguments.parse_args()

    cal.setfirstweekday(cal.SUNDAY)
    start = Month.from_datetime(datetime.now())
    for i in weeks(cycle(start, args.months)):
        print(i)
