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

from codecs import open
from setuptools import setup, find_packages
from tasksched import __version__ as tasksched_version

DESCRIPTION = 'Task scheduler with automatic resource leveling.'

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='tasksched',
    version=tasksched_version,
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Sébastien Helleu',
    author_email='flashcode@flashtux.org',
    url='https://github.com/tasksched/tasksched',
    license='GPL3',
    keywords='task scheduler planning automatic resource leveling',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 '
        'or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Scheduling',
    ],
    packages=find_packages(),
    package_data={
        'tasksched': [
            'data/html/*.html',
            'data/css/*.css',
        ],
    },
    install_requires=[
        'holidays',
        'jinja2',
        'pyyaml',
    ],
    tests_require=[
        'pytest',
    ],
    entry_points={
        'console_scripts': ['tasksched=tasksched:main'],
    }
)
