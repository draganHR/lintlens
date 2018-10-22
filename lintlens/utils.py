from __future__ import print_function, unicode_literals


def check_line_overlap_hunks(start, hunks, threshold):
    for change_from, change_to, _ in hunks:
        if check_line_in_range(start, change_to[0], change_to[1], threshold):
            return True
    return False


def check_line_in_range(line_number, range_start, range_count, threshold):
    in_range = range_start - threshold <= line_number <= range_start + range_count - 1 + threshold
    return in_range
