from __future__ import print_function, unicode_literals

from collections import namedtuple
import re

LintEntry = namedtuple('LintEntry', ['filename', 'line', 'column', 'message'])


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
