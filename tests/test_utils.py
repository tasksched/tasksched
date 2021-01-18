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
#

"""Tasksched utility tests."""

from datetime import date
import pytest

import holidays

from tasksched import (
    add_business_days,
    get_days,
    get_months,
    is_business_day as is_bus,
    string_to_date,
)


def test_is_business_day():
    """Test is_business_day function."""
    # business days (if no holidays given)
    assert is_bus(date(2020, 12, 21))  # Monday
    assert is_bus(date(2020, 12, 22))  # Tuesday
    assert is_bus(date(2020, 12, 23))  # Wednesday
    assert is_bus(date(2020, 12, 24))  # Thursday
    assert is_bus(date(2020, 12, 25))  # Friday

    # week-end
    assert is_bus(date(2020, 12, 26)) is False  # Saturday
    assert is_bus(date(2020, 12, 27)) is False  # Sunday

    # public holidays
    hdays = holidays.CountryHoliday('FRA', years=[2020, 2021])
    assert is_bus(date(2020, 12, 25), hdays) is False  # Christmas
    assert is_bus(date(2021, 1, 1), hdays) is False  # New Year's Day
    assert is_bus(date(2021, 5, 1), hdays) is False  # Labour Day


def test_add_business_days():
    """Test add_business_days function."""
    start = date(2020, 12, 21)  # Monday

    # no holidays
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


def test_get_days():
    """Test get_days function."""
    hdays = holidays.CountryHoliday('FRA', years=[2020, 2021])

    assert get_days(date(2020, 12, 21), date(2020, 12, 21), hdays) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
    }
    assert get_days(date(2020, 12, 21), date(2020, 12, 22), hdays) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
        date(2020, 12, 22): {'business_day': True, 'weekday': 'Tuesday'},
    }
    assert get_days(date(2020, 12, 21), date(2020, 12, 23), hdays) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
        date(2020, 12, 22): {'business_day': True, 'weekday': 'Tuesday'},
        date(2020, 12, 23): {'business_day': True, 'weekday': 'Wednesday'},
    }
    assert get_days(date(2020, 12, 21), date(2020, 12, 24), hdays) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
        date(2020, 12, 22): {'business_day': True, 'weekday': 'Tuesday'},
        date(2020, 12, 23): {'business_day': True, 'weekday': 'Wednesday'},
        date(2020, 12, 24): {'business_day': True, 'weekday': 'Thursday'},
    }
    assert get_days(date(2020, 12, 21), date(2020, 12, 25), hdays) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
        date(2020, 12, 22): {'business_day': True, 'weekday': 'Tuesday'},
        date(2020, 12, 23): {'business_day': True, 'weekday': 'Wednesday'},
        date(2020, 12, 24): {'business_day': True, 'weekday': 'Thursday'},
        date(2020, 12, 25): {'business_day': False, 'weekday': 'Friday'},
    }
    assert get_days(date(2020, 12, 21), date(2020, 12, 26), hdays) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
        date(2020, 12, 22): {'business_day': True, 'weekday': 'Tuesday'},
        date(2020, 12, 23): {'business_day': True, 'weekday': 'Wednesday'},
        date(2020, 12, 24): {'business_day': True, 'weekday': 'Thursday'},
        date(2020, 12, 25): {'business_day': False, 'weekday': 'Friday'},
        date(2020, 12, 26): {'business_day': False, 'weekday': 'Saturday'},
    }
    assert get_days(date(2020, 12, 21), date(2020, 12, 27), hdays) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
        date(2020, 12, 22): {'business_day': True, 'weekday': 'Tuesday'},
        date(2020, 12, 23): {'business_day': True, 'weekday': 'Wednesday'},
        date(2020, 12, 24): {'business_day': True, 'weekday': 'Thursday'},
        date(2020, 12, 25): {'business_day': False, 'weekday': 'Friday'},
        date(2020, 12, 26): {'business_day': False, 'weekday': 'Saturday'},
        date(2020, 12, 27): {'business_day': False, 'weekday': 'Sunday'},
    }
    assert get_days(date(2020, 12, 21), date(2020, 12, 28), hdays) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
        date(2020, 12, 22): {'business_day': True, 'weekday': 'Tuesday'},
        date(2020, 12, 23): {'business_day': True, 'weekday': 'Wednesday'},
        date(2020, 12, 24): {'business_day': True, 'weekday': 'Thursday'},
        date(2020, 12, 25): {'business_day': False, 'weekday': 'Friday'},
        date(2020, 12, 26): {'business_day': False, 'weekday': 'Saturday'},
        date(2020, 12, 27): {'business_day': False, 'weekday': 'Sunday'},
        date(2020, 12, 28): {'business_day': True, 'weekday': 'Monday'},
    }

    # no holidays
    assert get_days(date(2020, 12, 21), date(2020, 12, 28)) == {
        date(2020, 12, 21): {'business_day': True, 'weekday': 'Monday'},
        date(2020, 12, 22): {'business_day': True, 'weekday': 'Tuesday'},
        date(2020, 12, 23): {'business_day': True, 'weekday': 'Wednesday'},
        date(2020, 12, 24): {'business_day': True, 'weekday': 'Thursday'},
        date(2020, 12, 25): {'business_day': True, 'weekday': 'Friday'},
        date(2020, 12, 26): {'business_day': False, 'weekday': 'Saturday'},
        date(2020, 12, 27): {'business_day': False, 'weekday': 'Sunday'},
        date(2020, 12, 28): {'business_day': True, 'weekday': 'Monday'},
    }


def test_get_months():
    """Test get_months function."""
    assert get_months([date(2020, 12, 21), date(2020, 12, 22)]) == [
        ('December 2020', 31)
    ]
    assert get_months([
        date(2020, 12, 30),
        date(2020, 12, 31),
        date(2021, 1, 1),
    ]) == [
        ('December 2020', 31),
        ('January 2021', 31),
    ]
    assert get_months([
        date(2021, 2, 28),
        date(2021, 3, 1),
    ]) == [
        ('February 2021', 28),
        ('March 2021', 31),
    ]
    assert get_months([
        date(2024, 2, 29),
        date(2024, 3, 1),
    ]) == [
        ('February 2024', 29),
        ('March 2024', 31),
    ]


def test_string_to_date():
    """Test string_to_date function."""
    # default is today
    today = date.today()
    assert string_to_date(None) == today
    assert string_to_date('') == today

    # test with Christmas
    christmas = date(2020, 12, 25)
    assert string_to_date('2020-12-25') == christmas
    assert string_to_date(christmas) == christmas

    # test errors
    with pytest.raises(ValueError):
        string_to_date('xxx')
    with pytest.raises(TypeError):
        string_to_date(True)
    with pytest.raises(TypeError):
        string_to_date(123)
