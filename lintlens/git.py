from __future__ import print_function, unicode_literals

import subprocess

import re


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
