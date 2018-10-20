from __future__ import print_function, unicode_literals

from six.moves import range


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
