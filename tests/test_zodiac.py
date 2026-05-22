from constellation_core.zodiac import midpoint_longitude, shortest_arc, to_zodiac_position


def test_to_zodiac_position_capricorn():
    pos = to_zodiac_position(282.5)
    assert pos.sign == "Capricorn"
    assert pos.sign_index == 9
    assert pos.degree == 12.5


def test_shortest_arc_small_gap():
    assert shortest_arc(359, 1) == 2


def test_midpoint_standard():
    assert midpoint_longitude(10, 50) == 30
