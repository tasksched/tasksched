#!/usr/bin/env python3
#
# Copyright (C) 2020-2021 Sébastien Helleu <flashcode@flashtux.org>
#
# This file is part of Tasksched.
#
# Tasksched is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Tasksched is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Tasksched.  If not, see <https://www.gnu.org/licenses/>.

"""Utility functions for Tasksched."""

import calendar
import datetime

import yaml

__all__ = (
    'is_business_day',
    'add_business_days',
    'get_days',
    'get_months',
    'string_to_date',
    'yaml_dump',
)


def is_business_day(date, hdays=None):
    """
    Check if the date is a business day.

    :param datetime.date date: date to check
    :param dict hdays: list of dates with holidays
    :rtype: bool
    :return: True if the date is a business day, False otherwise (that means
        the date is either Saturday/Sunday or a public holiday)
    """
    return date.weekday() < 5 and date not in (hdays or {})


def add_business_days(from_date, count, hdays=None):
    """
    Add "count" business days to a date, skipping week-end days and public
    holidays.

    :param datetime.date from_date: start date
    :param int count: number of business days to add (≥ 0)
    :param dict hdays: list of dates with holidays
    :rtype: datetime.date
    :return: date with "count" business days added
    """
    to_add = count
    current_date = from_date
    while to_add > 0:
        current_date += datetime.timedelta(days=1)
        if not is_business_day(current_date, hdays):
            continue
        to_add -= 1
    return current_date


def get_days(from_date, to_date, hdays=None):
    """
    Return days between two dates, for each day the value is True for a
    business day, False for the other days.

    :param datetime.date from_date: start date
    :param datetime.date to_date: end date
    :param dict hdays: list of dates with holidays
    :rtype: dict
    :return: dictionary with days, keys are dates, values are dictionaries with
        keys: "weekday" (str) and "business_day" (bool)
    """
    days = {}
    current_date = from_date
    while current_date <= to_date:
        days[current_date] = {
            'weekday': current_date.strftime('%A'),
            'business_day': is_business_day(current_date, hdays),
        }
        current_date += datetime.timedelta(days=1)
    return days


def get_months(days):
    """
    Return a dictionary with month as key and the number of days in each
    months, for a list of days.

    :param dict days: dictionary with days: key is a datetime.date and value
        is True if it's a business day, False otherwise
    :rtype: dict
    :return: dictionary with key
    """
    months = []
    prev_month = -1
    for day in days:
        if day.month != prev_month:
            name = f'{calendar.month_name[day.month]} {day.year}'
            days_in_month = calendar.monthrange(day.year, day.month)[1]
            months.append((name, days_in_month))
        prev_month = day.month
    return months


def string_to_date(the_date):
    """
    Convert the date to a datetime.date object (except if it's already a date
    object.

    :param str,datetime.date: date
    :rtype: datetime.date
    :return: date as datetime.date (today if date is None or empty)
    """
    if not the_date:
        return datetime.date.today()
    if isinstance(the_date, datetime.date):
        return the_date
    return datetime.date.fromisoformat(the_date)


def yaml_dump(data):
    """
    Dump dictionary to a YAML string.

    :param dict data: data
    :rtype: str
    :return: YAML as string, keys are not sorted (same order as the dict),
        no aliases in the YAML output
    """
    yaml.Dumper.ignore_aliases = lambda *args: True
    return yaml.dump(data, sort_keys=False)
