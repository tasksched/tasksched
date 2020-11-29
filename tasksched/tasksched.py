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
import sys

from tasksched.project import Project
from tasksched.workplan import build_workplan
from tasksched.workplan_text import workplan_to_text

__version__ = '0.3.0'

__all__ = (
    '__version__',
    'load_config',
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


def get_input_files(args):
    """
    Get list of input files (optional stdin file + filenames).

    :rtype: list
    :return: list of files/filenames
    """
    files = []
    if not sys.stdin.isatty():
        files.append(sys.stdin)
    files.extend(args.filename)
    return files


def read_json(json_file):
    """
    Read JSON file.

    :param object,str json_file: file or filename
    :rtype: dict
    :return: JSON file as dict
    """
    try:
        if isinstance(json_file, str):
            with open(json_file) as _file:
                return json.load(_file)
        else:
            return json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as exc:
        if isinstance(json_file, str):
            fatal(f'ERROR: unable to decode JSON file "{json_file}": {exc}')
        else:
            fatal(f'ERROR: unable to decode JSON: {exc}')


def search_item(list_items, item_id):
    """
    Search an item by its id in a list.

    :param list list_items: list of items
    :param str item_id: item id to search in the list of items
    :rtype: object
    :return: the item found or None
    """
    if item_id:
        for item in list_items:
            if item['id'] == item_id:
                return item
    return None


def merge_configs(config, new_config):
    """
    Merge config2 into config: each value in config is updated with value
    from config2: for dicts (like "project"), keys are updated, for lists
    (like "resources" or "tasks"), items are added to the list.

    :param dict config: first config to update
    :param dict new_config: dictionary used to update the config
    """
    for key, value in new_config.items():
        if key not in config:
            config[key] = value
            continue
        if isinstance(config[key], dict):
            if not isinstance(value, dict):
                raise ValueError(f'merge config error: '
                                 f'cannot update dict "{key}"')
            config[key].update(value)
        elif isinstance(config[key], list):
            if not isinstance(value, list):
                raise ValueError(f'merge config error: '
                                 f'cannot update list "{key}"')
            for item in value:
                if isinstance(item, dict):
                    config_item = search_item(config[key], item.get('id'))
                    if config_item is None:
                        config[key].append(item)
                    else:
                        config_item.update(item)
                else:
                    config[key].append(item)
        else:
            config[key] = value


def load_config(files):
    """
    Load JSON configuration by reading stdin (if availbale) and list of input
    files received on command line.

    :param list files: JSON files/filenames to load
    :rtype: dict
    :return: configuration
    """
    config = {}
    for _file in files:
        new_config = read_json(_file)
        merge_configs(config, new_config)
    return config


def fatal(error):
    """
    Display a fatal error and exit with return code 1.

    :param str error: error to display
    """
    print(error, file=sys.stderr)
    print('Try with --help to get help on tasksched', file=sys.stderr)
    sys.exit(1)


def action_workplan(args):
    """
    Return the work plan (as JSON) using the project configuration.

    :param argparse.Namespace args: command-line arguments
    """
    files = get_input_files(args)
    config = load_config(files)
    try:
        project = Project(config)
    except (KeyError, ValueError) as exc:
        fatal(f'ERROR: invalid project, missing data: "{exc.args[0]}"')
    workplan = build_workplan(project)
    return json.dumps(workplan.as_dict())


def action_text(args):
    """
    Return the work plan as text to display in the terminal.

    :param argparse.Namespace args: command-line arguments
    """
    files = get_input_files(args)
    if not files:
        fatal('ERROR: missing input workplan')
    config = read_json(files[-1])
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
    result = func(args)
    print(result)


def init(force=False):
    """Init function."""
    if __name__ == '__main__' or force:
        main()


init()
