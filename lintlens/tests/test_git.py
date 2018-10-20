from __future__ import print_function, unicode_literals

from ..git import parse_hunk, parse_file_line_numbers


def test_parse_hunk():
    assert parse_hunk('@@ -0 +1 @@ Foo bar') == ((0, 1), (1, 1), u'Foo bar')
    assert parse_hunk('@@ -987 +99999 @@ Foo bar') == ((987, 1), (99999, 1), u'Foo bar')
    assert parse_hunk('@@ -5,0 +42,5 @@ Foo bar') == ((5, 0), (42, 5), u'Foo bar')
    assert parse_hunk('@@ -1,3 +42,0 @@ Foo bar') == ((1, 3), (42, 0), u'Foo bar')
    assert parse_hunk('@@ -0 +1 @@') == ((0, 1), (1, 1), u'')


def test_parse_file_line_numbers():
    assert parse_file_line_numbers('-0') == (0, 1)
    assert parse_file_line_numbers('+0') == (0, 1)
    assert parse_file_line_numbers('+0,0') == (0, 0)
    assert parse_file_line_numbers('+0,1') == (0, 1)
    assert parse_file_line_numbers('+0,5') == (0, 5)
    assert parse_file_line_numbers('+123,5') == (123, 5)
