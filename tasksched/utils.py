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


def add_business_days(from_date, count, dict_holidays=None):
    """
    Add "count" business days to a date, skipping week-end days and public
    holidays.

    :param datetime.date from_date: start date
    :param int count: number of business days to add (≥ 0)
    :param dict dict_holidays: list of dates with holidays (these days are
         skipped)
    """
    hdays = dict_holidays or {}
    to_add = count
    current_date = from_date
    while to_add > 0:
        current_date += datetime.timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5 or current_date in hdays:
            continue
        to_add -= 1
    return current_date
