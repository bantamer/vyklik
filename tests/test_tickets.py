from vyklik.bot import tickets


def test_parse():
    assert tickets.parse("k50") == ("K", 50)
    assert tickets.parse("G045") == ("G", 45)
    assert tickets.parse("nonsense") is None


def test_distance_same_series():
    assert tickets.distance("K090", "K080") == 10
    assert tickets.distance("K080", "K090") == -10


def test_distance_different_series_is_none():
    assert tickets.distance("K090", "D052") is None


def test_wrong_series_blocks_mismatch():
    # K-ticket in a D-series queue (the real prod case)
    assert tickets.wrong_series("K50", "D") is True


def test_wrong_series_allows_match_case_insensitive():
    assert tickets.wrong_series("k080", "K") is False
    assert tickets.wrong_series("K080", "k") is False


def test_wrong_series_never_blocks_on_uncertainty():
    assert tickets.wrong_series("K080", None) is False  # queue prefix unknown
    assert tickets.wrong_series("garbage", "K") is False  # unparseable ticket
