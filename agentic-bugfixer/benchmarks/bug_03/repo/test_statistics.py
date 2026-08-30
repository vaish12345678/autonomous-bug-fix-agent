from statistics import calculate_average


def test_integer_average():
    assert calculate_average([10, 20, 30]) == 20


def test_decimal_average():
    assert calculate_average([10, 20, 25]) == 18.333333333333332


def test_single_number():
    assert calculate_average([50]) == 50