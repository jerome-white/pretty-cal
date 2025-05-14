import operator as op
import calendar as cal
import itertools as it
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
        return '{} {}'.format(cal.month_abbr[self.month].upper(), self.year)

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

    def __str__(self):
        header = str(self.month)
        if not self.start:
            header = ' ' * len(header)
        body = ('{:>2}'.format(x if x else '') for x in self.days)

        return '{}{}{}'.format(header, ' ' * 3, ' '.join(body))

    def full(self):
        return all(self.days)

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
    args = arguments.parse_args()

    cal.setfirstweekday(cal.SUNDAY)
    start = Month.from_datetime(datetime.now())
    for i in combine(weeks(start, args.months)):
        print(i)
