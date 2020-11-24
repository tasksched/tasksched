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

"""Task scheduler with automatic resource leveling."""

import argparse
import json
import select
import sys

from tasksched.project import Project
from tasksched.workplan import build_workplan
from tasksched.workplan_text import workplan_to_text

__version__ = '0.1.0'

__all__ = (
    '__version__',
    'main',
    'init',
)


def get_parser():
    """
    Return the parser for command line options.

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
        version=__version__,
    )

    help_filename = (
        'JSON configuration filename; if multiple files are given, '
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
        'filename',
        nargs='*',
        help=help_filename,
    )
    parser_workplan.set_defaults(action='workplan')

    # action: "text"
    parser_text = subparsers.add_parser(
        'text',
        add_help=False,
        help='display the work plan as text',
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
    return parser


def get_config(args):
    """
    Get JSON configuration by reading stdin (if availbale) and list of input
    files received on command line.

    :param argparse.Namespace args: command-line arguments
    """
    config = {}
    inr = select.select([sys.stdin], [], [], 0.1)[0]
    if inr:
        json_data = sys.stdin.read(200000)
        try:
            config.update(json.loads(json_data))
        except json.decoder.JSONDecodeError as exc:
            fatal(f'ERROR: unable to decode JSON on stdin: {exc}')
    for filename in args.filename:
        try:
            with open(filename) as json_file:
                config.update(json.load(json_file))
        except (FileNotFoundError, json.decoder.JSONDecodeError) as exc:
            fatal(f'ERROR: unable to decode JSON file "{filename}": {exc}')
    return config


def fatal(error):
    """
    Display a fatal error and exit with return code 1.

    :param str error: error to display
    """
    print(error, file=sys.stderr)
    print('Try with --help to get help on tasksched', file=sys.stderr)
    sys.exit(1)


def action_workplan(args, config):  # pylint: disable=unused-argument
    """
    Return the work plan (as JSON) using the project configuration.

    :param argparse.Namespace args: command-line arguments
    :param dict config: project configuration
    """
    try:
        project = Project(config)
    except (KeyError, ValueError) as exc:
        fatal(f'ERROR: invalid project, missing data: "{exc.args[0]}"')
    workplan = build_workplan(project)
    return json.dumps(workplan.as_dict())


def action_text(args, config):
    """
    Return the work plan as text to display in the terminal.

    :param argparse.Namespace args: command-line arguments
    :param dict config: work plan
    """
    try:
        return workplan_to_text(
            config,
            use_colors=not args.no_colors,
            use_unicode=not args.no_unicode,
        )
    except (KeyError, ValueError) as exc:
        fatal(f'ERROR: invalid work plan, missing data: "{exc}"')


def main():
    """Main function, entry point."""
    args = get_parser().parse_args()
    func = getattr(sys.modules[__name__], f'action_{args.action}')
    result = func(args, get_config(args))
    print(result)


def init(force=False):
    """Init function."""
    if __name__ == '__main__' or force:
        main()


init()
