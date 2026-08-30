from calculator import divide


def test_divide():
    assert divide(10, 2) == 5


def test_divide_small_numbers():
    assert divide(8, 2) == 4