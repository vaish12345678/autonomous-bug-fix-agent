from parity_checker import is_even


def test_even_number():
    assert is_even(4) is True


def test_odd_number():
    assert is_even(5) is False


def test_zero():
    assert is_even(0) is True