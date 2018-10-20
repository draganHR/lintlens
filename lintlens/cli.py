#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""...
"""
from __future__ import print_function, unicode_literals
import re
import argparse
import subprocess
import codecs
from collections import namedtuple

from six.moves import range


LintEntry = namedtuple('LintEntry', ['filename', 'start', 'count', 'content'])


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


def parse_lint_line(line):
    """Parse lint diff line

    >>> parse_lint_line('foo.txt:1:2: bar')
    LintEntry(filename=u'foo.txt', start=1, count=2, content=u'bar')

    >>> parse_lint_line('foo.txt:123:50: bar')
    LintEntry(filename=u'foo.txt', start=123, count=50, content=u'bar')

    >>> parse_lint_line('foo.txt:0:1:')
    LintEntry(filename=u'foo.txt', start=0, count=1, content=u'')

    >>> parse_lint_line('foo/foo bar.txt:0:1: baz')
    LintEntry(filename=u'foo/foo bar.txt', start=0, count=1, content=u'baz')
    """
    # TODO: handle colon in filename
    line_parts = re.match('(?:\./)?(.+?):(\d+):(\d+): ?(.*)', line)
    lint_entry = LintEntry(
        line_parts.group(1),
        int(line_parts.group(2)),
        int(line_parts.group(3)),
        line_parts.group(4)
    )
    return lint_entry


def get_diff_lines(revision_range):
    cmd_output = subprocess.check_output(['git', 'diff', revision_range, '--unified=0'],
                                         universal_newlines=True)
    cmd_output = cmd_output.decode('utf-8')

    lines = cmd_output.split('\n')

    a_filename, b_filename = None, None
    hunks = None

    for line in lines:
        if line.startswith('diff --git'):
            # Process next file
            if hunks:
                yield (a_filename, b_filename), hunks
            hunks = []

        elif line.startswith('--- '):
            a_filename = parse_git_diff_filename(line)

        elif line.startswith('+++ '):
            b_filename = parse_git_diff_filename(line)

        elif line.startswith('@@'):
            hunk = parse_hunk(line)
            hunks.append(hunk)

    # Last file
    if hunks:
        yield (a_filename, b_filename), hunks


def parse_git_diff_filename(line):
    line_decoded = line.decode('unicode-escape').encode('latin-1').decode('utf-8')
    without_prefix = line_decoded[4:].rstrip()
    if without_prefix == '/dev/null':
        return ''
    without_quotes = without_prefix[1:-1] if without_prefix.startswith('"') else without_prefix
    filename = without_quotes[2:]  # Strip a/b
    return filename


def parse_hunk(line):
    """Parse git hunk

    >>> parse_hunk('@@ -0 +1 @@ Foo bar')
    ((0, 1), (1, 1), u'Foo bar')

    >>> parse_hunk('@@ -987 +99999 @@ Foo bar')
    ((987, 1), (99999, 1), u'Foo bar')

    >>> parse_hunk('@@ -5,0 +42,5 @@ Foo bar')
    ((5, 0), (42, 5), u'Foo bar')

    >>> parse_hunk('@@ -1,3 +42,0 @@ Foo bar')
    ((1, 3), (42, 0), u'Foo bar')

    >>> parse_hunk('@@ -0 +1 @@')
    ((0, 1), (1, 1), u'')
    """
    hunk_parts = re.match(r"^@@ ([^@ ]+) ([^@ ]+) @@ ?(.*)$", line)
    line_from_formatted, line_to_formatted, code = hunk_parts.groups()

    line_from = parse_file_line_numbers(line_from_formatted)
    line_to = parse_file_line_numbers(line_to_formatted)

    return line_from, line_to, code


def parse_file_line_numbers(formatted_numbers):
    """
    Parse "start,count" formatted line numbers

    >>> parse_file_line_numbers('-0')
    (0, 1)

    >>> parse_file_line_numbers('+0')
    (0, 1)

    >>> parse_file_line_numbers('+0,0')
    (0, 0)

    >>> parse_file_line_numbers('+0,1')
    (0, 1)

    >>> parse_file_line_numbers('+0,5')
    (0, 5)

    >>> parse_file_line_numbers('+123,5')
    (123, 5)
    """
    formatted = formatted_numbers[1:]  # strip -/+
    formatted_parts = formatted.split(',')
    start = int(formatted_parts[0])
    count = int(formatted_parts[1]) if len(formatted_parts) > 1 else 1
    return start, count


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
