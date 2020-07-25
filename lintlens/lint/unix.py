from __future__ import print_function, unicode_literals

import re
from collections import namedtuple

LintEntry = namedtuple('LintEntry', ['filename', 'line', 'column', 'message'])

line_parts_pattern = re.compile(r'(?:\./)?(.+?):(\d+):(\d+): ?(.*)')


def parse_lint_line(line):
    """Parse lint diff line

    >>> parse_lint_line('foo.txt:1:2: bar')
    LintEntry(filename='foo.txt', line=1, column=2, message='bar')

    >>> parse_lint_line('foo.txt:123:50: bar')
    LintEntry(filename='foo.txt', line=123, column=50, message='bar')

    >>> parse_lint_line('foo.txt:0:1:')
    LintEntry(filename='foo.txt', line=0, column=1, message='')

    >>> parse_lint_line('foo/foo bar.txt:0:1: baz')
    LintEntry(filename='foo/foo bar.txt', line=0, column=1, message='baz')
    """
    # TODO: handle colon in filename
    line_parts = line_parts_pattern.match(line)
    lint_entry = LintEntry(
        line_parts.group(1),
        int(line_parts.group(2)),
        int(line_parts.group(3)),
        line_parts.group(4)
    )
    return lint_entry
