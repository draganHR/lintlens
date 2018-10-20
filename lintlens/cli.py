#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""...
"""
from __future__ import print_function, unicode_literals
import re
import argparse
import codecs

from six.moves import range

from .git import get_diff_lines
from .linting import parse_lint_line


def handle_range(revision_range, lint_lines):
    diff_lines = {}
    for filename, hunks in get_diff_lines(revision_range):
        diff_lines[filename[1]] = hunks

    for lint_line in lint_lines:
        lint_entry = parse_lint_line(lint_line)

        # skip file not changed in revision_range
        if lint_entry.filename not in diff_lines:
            continue

        hunks = diff_lines[lint_entry.filename]
        if check_line_overlap_hunks(lint_entry.start, lint_entry.count, hunks):
            print(lint_line.encode('utf-8'), end='')


def check_line_overlap_hunks(start, count, hunks):
    for change_from, change_to, _ in hunks:
        if check_line_overlap_range(start, count, change_to[0], change_to[1]):
            return True
    return False


def check_line_overlap_range(start, count, range_start, range_count):
    threshold = 1
    for line_number in range(start, start + count + 1):
        if range_start - threshold <= line_number <= range_start + range_count + threshold:
            return True
    return False


def read_file_lines(filename):
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines


def main():
    parser = argparse.ArgumentParser(prog='lintlens',
                                     description=__doc__)
    parser.add_argument('revision_range',
                        help='Include changes in the specified revision range.')
    parser.add_argument('input_filename',
                        help='Input filename')

    args = parser.parse_args()

    lint_lines = read_file_lines(args.input_filename)

    handle_range(args.revision_range, lint_lines)


if __name__ == "__main__":
    main()
