import operator as op
import calendar as cal
import itertools as it
import functools as ft
from typing import ClassVar
from datetime import datetime
from argparse import ArgumentParser
from dataclasses import dataclass, replace

@dataclass
class Month:
    month: int
    year: int
    _months: ClassVar[int] = len(cal.month_name) - 1

    def __add__(self, months):
        month = self.month + months
        if month > self._months:
            month %= self._months
            year = self.year + 1
        else:
            year = self.year

        return type(self)(month, year)

    def __str__(self):
        return '{} {}'.format(cal.month_abbr[self.month], self.year)

    @classmethod
    def from_datetime(cls, dt):
        return cls(dt.month, dt.year)

@dataclass
class Week:
    month: Month
    days: list
    start: bool = False

    def __post_init__(self):
        try:
            index = self.days.index(1)
        except ValueError:
            index = None
        self.start = index is not None

    def __iter__(self):
        yield from self.days

    def full(self):
        return all(self)

class WeekFormatter:
    @ft.cached_property
    def dnames(self):
        n = len(cal.day_abbr)

        iterable = map(op.itemgetter(0), enumerate(cal.day_abbr, 1))
        week = (cal.day_name[x % n][:self.dlen] for x in iterable)
        return list(self.days(week))

    def __init__(self, sep, dlen):
        self.m_sep = ' ' * sep
        self.dlen = dlen

    def __call__(self, week, header=False):
        month = str(week.month)
        if not week.start:
            month = ' ' * len(month)
        day = ' '.join(self.days(week))

        wstring = [
            self.line(month, day)
        ]
        if header:
            m = ' ' * len(month)
            w = ' '.join(self.dnames)
            wstring.append(self.line(m, w))

        return '\n'.join(reversed(wstring))

    def days(self, week):
        for w in week:
            d = str(w if w else '')
            yield d.rjust(self.dlen)

    def line(self, month, week):
        return '{}{}{}'.format(month, self.m_sep, week)

def weeks(month, n):
    for _ in range(n):
        for i in cal.monthcalendar(month.year, month.month):
            yield Week(month, i)
        month += 1

def combine(weeks):
    last_w = None

    for (i, this_w) in enumerate(weeks):
        if not i or this_w.full():
            yield this_w
        elif last_w is None:
            last_w = this_w
        else:
            days = it.starmap(op.add, zip(last_w.days, this_w.days))
            yield replace(this_w, days=list(days))
            last_w = None

    if last_w is not None:
        yield last_w

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--months', type=int)
    arguments.add_argument('--month-week-sep', type=int, default=1)
    args = arguments.parse_args()

    cal.setfirstweekday(cal.SUNDAY)
    start = Month.from_datetime(datetime.now())
    formatter = WeekFormatter(args.month_week_sep)
    for (i, w) in enumerate(combine(weeks(start, args.months))):
        print(formatter(w, not i))
