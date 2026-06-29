from vyklik.bot.keyboards import rearm_threshold


def _callbacks(markup) -> list[str]:
    return [b.callback_data for row in markup.inline_keyboard for b in row]


def test_rearm_ladder_below_dist():
    kb = rearm_threshold(42, 10, "ru")
    assert _callbacks(kb) == ["rearm:42:5", "rearm:42:3", "rearm:42:2", "rearm:42:1"]


def test_rearm_small_dist():
    kb = rearm_threshold(7, 2, "ru")
    assert _callbacks(kb) == ["rearm:7:1"]


def test_rearm_none_when_nothing_tighter():
    assert rearm_threshold(7, 1, "ru") is None
