from discount import calculate_discount


def test_discount():
    assert calculate_discount(100, 20) == 80


def test_larger_price():
    assert calculate_discount(1000, 25) == 750


def test_small_discount():
    assert calculate_discount(500, 10) == 450


def test_full_discount():
    assert calculate_discount(200, 100) == 0