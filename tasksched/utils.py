#!/usr/bin/env python3
#
# Copyright (C) 2020 Sébastien Helleu <flashcode@flashtux.org>
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

import datetime

__all__ = (
    'is_business_day',
    'add_business_days',
)


def is_business_day(date, hdays=None):
    """
    Check if the date is a business day.

    :param datetime.date date: date to check
    :param dict hdays: list of dates with holidays
    :rtype: bool
    :return: True if the date is a business day, False otherwise (that means
        the date is either saturday/sunday or a public holiday)
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
