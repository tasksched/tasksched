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

"""Task scheduler command line parser."""

import argparse

__all__ = (
    'get_parser',
)


def get_parser(tasksched_version):
    """
    Return the parser for command line options.

    :param str tasksched_version: tasksched version
    :rtype: argparse.ArgumentParser
    :return: argument parser
    """
    # pylint: disable=protected-access,too-few-public-methods
    class HelpAction(argparse._HelpAction):
        """Custom help on argument parser."""

        def __call__(self, parser, namespace, values, option_string=None):
            parser.print_help()
            print()
            print('Sub-actions:')
            print()
            subparsers_actions = [
                action for action in parser._actions
                if isinstance(action, argparse._SubParsersAction)
            ]
            for subparsers_action in subparsers_actions:
                for choice, subparser in subparsers_action.choices.items():
                    print(f'  ----- tasksched {choice} -----')
                    print('  |')
                    print('\n'.join([
                        '  |  %s' % line
                        for line in subparser.format_help().split('\n')
                    ]))
            parser.exit()

    # main parser
    parser = argparse.ArgumentParser(
        description='Task scheduler with automatic resource leveling.',
        add_help=False,
    )
    parser.add_argument('-h', '--help',
                        action=HelpAction,
                        help='show help message and exit')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=tasksched_version,
    )

    help_filename = (
        'YAML/JSON configuration filename; if multiple files are given, '
        'they are loaded in order the each file content is added to '
        'the previous ones; if available, the standard input content '
        'is loaded before these files'
    )

    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True

    # action: "workplan"
    parser_workplan = subparsers.add_parser(
        'workplan',
        add_help=False,
        help='build the work plan with the project',
    )
    parser_workplan.add_argument(
        '-j', '--json',
        action='store_true',
        help='return JSON instead of YAML',
    )
    parser_workplan.add_argument(
        'filename',
        nargs='*',
        help=help_filename,
    )
    parser_workplan.set_defaults(action='workplan')

    # action: "text"
    parser_text = subparsers.add_parser(
        'text',
        add_help=False,
        help='convert the work plan to text',
    )
    parser_text.add_argument(
        '-c', '--no-colors',
        action='store_true',
        help='do not use colors in output',
    )
    parser_text.add_argument(
        '-u', '--no-unicode',
        action='store_true',
        help='do not use unicode chars in output',
    )
    parser_text.add_argument(
        'filename',
        nargs='*',
        help=help_filename,
    )
    parser_text.set_defaults(action='text')

    # action: "html"
    parser_text = subparsers.add_parser(
        'html',
        add_help=False,
        help='convert the work plan to HTML',
    )
    parser_text.add_argument(
        '-t', '--template',
        default='basic',
        help='template name or path',
    )
    parser_text.add_argument(
        '-c', '--css',
        default='dark',
        help='CSS name or path',
    )
    parser_text.add_argument(
        'filename',
        nargs='*',
        help=help_filename,
    )
    parser_text.set_defaults(action='html')

    return parser
