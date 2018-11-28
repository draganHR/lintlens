from __future__ import print_function, unicode_literals

import subprocess
import re

import six


def get_diff_lines(revision_range):
    diff_content = get_diff(revision_range)
    for entry in parse_diff(diff_content):
        yield entry


def get_diff(revision_range):
    cmd_output = subprocess.check_output(['git', 'diff', revision_range, '--unified=0'],
                                         universal_newlines=True)
    if isinstance(cmd_output, six.binary_type):
        cmd_output = cmd_output.decode('utf-8')
    return cmd_output


def parse_diff(diff_content):
    lines = diff_content.split('\n')

    a_filename, b_filename = None, None
    hunks = None

    for line in lines:
        if line.startswith('diff --git'):
            # Process next file
            if hunks:
                yield (a_filename, b_filename), hunks
            hunks = []

        elif line.startswith('--- '):
            a_filename = parse_diff_filename(line)

        elif line.startswith('+++ '):
            b_filename = parse_diff_filename(line)

        elif line.startswith('@@'):
            hunk = parse_hunk(line)
            hunks.append(hunk)

    # Last file
    if hunks:
        yield (a_filename, b_filename), hunks


def parse_diff_filename(line):
    if isinstance(line, six.binary_type):
        line = line.decode('unicode-escape')
    line_decoded = line.encode('latin-1').decode('utf-8')
    without_prefix = line_decoded[4:].rstrip()
    if without_prefix == '/dev/null':
        return ''
    without_quotes = without_prefix[1:-1] if without_prefix.startswith('"') else without_prefix
    filename = without_quotes[2:]  # Strip a/b
    return filename


def parse_hunk(line):
    """
    Parse git hunk (Example: "@@ -5,0 +42,5 @@ Foobar")
    """
    hunk_parts = re.match(r"^@@ ([^@ ]+) ([^@ ]+) @@ ?(.*)$", line)
    line_from_formatted, line_to_formatted, code = hunk_parts.groups()

    line_from = parse_file_line_numbers(line_from_formatted)
    line_to = parse_file_line_numbers(line_to_formatted)

    return line_from, line_to, code


def parse_file_line_numbers(formatted_numbers):
    """
    Parse "start,count" formatted line numbers
    """
    formatted = formatted_numbers[1:]  # strip -/+
    formatted_parts = formatted.split(',')
    start = int(formatted_parts[0])
    count = int(formatted_parts[1]) if len(formatted_parts) > 1 else 1
    return start, count
