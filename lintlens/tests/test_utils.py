import pytest

from lintlens.utils import check_line_in_range


def test_check_line_in_range_first_line():
    args = 1, 1, 0
    assert check_line_in_range(0, *args) is False
    assert check_line_in_range(1, *args) is True
    assert check_line_in_range(2, *args) is False


@pytest.mark.parametrize('range_count', (1, 2, 3, 4, 5))
def test_check_line_in_range_for_range_count(range_count):
    args = 42, range_count, 0
    for i in range(3):
        assert check_line_in_range(41 - i, *args) is False
    for i in range(range_count):
        assert check_line_in_range(42 + i, *args) is True
    for i in range(3):
        assert check_line_in_range(43 + i + range_count, *args) is False
