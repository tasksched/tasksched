#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2020-2025 Sébastien Helleu <flashcode@flashtux.org>
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

"""Task scheduler command line parser."""

import argparse

__all__ = (
    "get_parser",
)


def add_text_options(
    parser: argparse.ArgumentParser, action: str, help_filename: str
):
    """
    Add options for "text" or "workplan_text" actions.

    :param parser: the parser
    :param action: the action ("workplan_text" or "text")
    :param help_filename: help on filename option
    """
    parser.add_argument(
        "-c",
        "--no-colors",
        action="store_true",
        help="do not use colors in output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="display only work plan summary info (no legend/tasks)",
    )
    parser.add_argument(
        "-u",
        "--no-unicode",
        action="store_true",
        help="do not use unicode chars in output",
    )
    parser.add_argument(
        "filename",
        nargs="*",
        help=help_filename,
    )
    parser.set_defaults(action=action)


def add_html_options(
    parser: argparse.ArgumentParser, action: str, help_filename: str
):
    """
    Add options for "html" or "workplan_html" actions.

    :param parser: the parser
    :param action: the action ("workplan_html" or "html")
    :param help_filename: help on filename option
    """
    parser.add_argument(
        "-t",
        "--template",
        default="basic",
        help="template name or path",
    )
    parser.add_argument(
        "-c",
        "--css",
        default="dark",
        help="CSS name or path",
    )
    parser.add_argument(
        "filename",
        nargs="*",
        help=help_filename,
    )
    parser.set_defaults(action=action)


def get_parser(tasksched_version: str) -> argparse.ArgumentParser:
    """
    Return the parser for command line options.

    :param tasksched_version: tasksched version
    :return: argument parser
    """
    # pylint: disable=protected-access,too-few-public-methods
    class HelpAction(argparse._HelpAction):
        """Custom help on argument parser."""

        def __call__(self, parser, namespace, values, option_string=None):
            parser.print_help()
            print()
            print("Sub-actions:")
            print()
            subparsers_actions = [
                action
                for action in parser._actions
                if isinstance(action, argparse._SubParsersAction)
            ]
            for subparsers_action in subparsers_actions:
                for choice, subparser in subparsers_action.choices.items():
                    print(f"  ----- tasksched {choice} -----")
                    print("  |")
                    print(
                        "\n".join(
                            [
                                f"  |  {line}"
                                for line in subparser.format_help().split(
                                    "\n"
                                )
                            ]
                        )
                    )
            parser.exit()

    # main parser
    parser = argparse.ArgumentParser(
        description="Task scheduler with automatic resource leveling.",
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action=HelpAction, help="show help message and exit"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=tasksched_version,
    )

    help_filename = (
        "YAML/JSON configuration filename; if multiple files are given, "
        "they are loaded in order the each file content is added to "
        "the previous ones; if available, the standard input content "
        "is loaded before these files"
    )

    subparsers = parser.add_subparsers(dest="action")
    subparsers.required = True

    # action: "workplan"
    parser_workplan = subparsers.add_parser(
        "workplan",
        add_help=False,
        help="build the work plan with the project",
    )
    parser_workplan.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="return JSON instead of YAML",
    )
    parser_workplan.add_argument(
        "filename",
        nargs="*",
        help=help_filename,
    )
    parser_workplan.set_defaults(action="workplan")

    # action: "text"
    parser_text = subparsers.add_parser(
        "text",
        add_help=False,
        help="convert the work plan to text",
    )
    add_text_options(parser_text, "text", help_filename)

    # action: "html"
    parser_html = subparsers.add_parser(
        "html",
        add_help=False,
        help="convert the work plan to HTML",
    )
    add_html_options(parser_html, "html", help_filename)

    # action: "workplan_text"
    parser_workplan_text = subparsers.add_parser(
        "workplan_text",
        add_help=False,
        help=(
            "build the work plan and convert it to text "
            "(shortcut of workplan + text actions)"
        ),
    )
    add_text_options(parser_workplan_text, "workplan_text", help_filename)

    # action: "workplan_html"
    parser_workplan_html = subparsers.add_parser(
        "workplan_html",
        add_help=False,
        help=(
            "build the work plan and convert it to HTML "
            "(shortcut of workplan + html actions)"
        ),
    )
    add_html_options(parser_workplan_html, "workplan_html", help_filename)

    return parser
