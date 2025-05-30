#
# SPDX-FileCopyrightText: 2021-2025 Sébastien Helleu <flashcode@flashtux.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

all: check

check: lint test

lint: flake8 pylint mypy bandit

flake8:
	flake8 tasksched tests/*.py --count --select=E9,F63,F7,F82 --ignore=E203,W503 --show-source --statistics
	flake8 tasksched tests/*.py --count --ignore=E203,W503 --exit-zero --max-complexity=10 --statistics

pylint:
	pylint tasksched
	pylint tests

mypy:
	mypy tasksched
	mypy tests

bandit:
	bandit -r tasksched

test:
	pytest -vv --cov-report term-missing --cov=tasksched tests
