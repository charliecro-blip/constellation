from constellation_core.aspects import detect_aspect


def test_detect_conjunction():
    aspect = detect_aspect("venus", 10, "ascendant", 12)
    assert aspect is not None
    assert aspect.aspect == "conjunction"
    assert aspect.orb == 2


def test_detect_opposition():
    aspect = detect_aspect("moon", 2, "moon", 182)
    assert aspect is not None
    assert aspect.aspect == "opposition"
    assert aspect.orb == 0


def test_no_aspect_outside_orb():
    aspect = detect_aspect("venus", 10, "mars", 44)
    assert aspect is None
