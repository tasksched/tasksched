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
#

"""Tasksched utility tests."""

from datetime import date

import holidays


def test_add_business_days():
    """Test add_business_days function."""
    from tasksched import add_business_days

    start = date(2020, 12, 21)  # monday

    # no holdays
    assert add_business_days(start, 1) == date(2020, 12, 22)
    assert add_business_days(start, 2) == date(2020, 12, 23)
    assert add_business_days(start, 3) == date(2020, 12, 24)
    assert add_business_days(start, 4) == date(2020, 12, 25)
    assert add_business_days(start, 5) == date(2020, 12, 28)
    assert add_business_days(start, 6) == date(2020, 12, 29)
    assert add_business_days(start, 7) == date(2020, 12, 30)
    assert add_business_days(start, 8) == date(2020, 12, 31)
    assert add_business_days(start, 9) == date(2021, 1, 1)
    assert add_business_days(start, 10) == date(2021, 1, 4)

    # French holidays
    hdays = holidays.CountryHoliday('FRA', years=[2020, 2021])
    assert add_business_days(start, 1, hdays) == date(2020, 12, 22)
    assert add_business_days(start, 2, hdays) == date(2020, 12, 23)
    assert add_business_days(start, 3, hdays) == date(2020, 12, 24)
    assert add_business_days(start, 4, hdays) == date(2020, 12, 28)
    assert add_business_days(start, 5, hdays) == date(2020, 12, 29)
    assert add_business_days(start, 6, hdays) == date(2020, 12, 30)
    assert add_business_days(start, 7, hdays) == date(2020, 12, 31)
    assert add_business_days(start, 8, hdays) == date(2021, 1, 4)
    assert add_business_days(start, 9, hdays) == date(2021, 1, 5)
    assert add_business_days(start, 10, hdays) == date(2021, 1, 6)
