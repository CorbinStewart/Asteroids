from game_clock import GameClock


def test_game_clock_scales_dt():
    clock = GameClock()

    assert clock.scale_dt(1.0) == 1.0

    clock.set_time_scale(0.5)
    assert clock.scale_dt(2.0) == 1.0

    clock.reset_time_scale()
    assert clock.scale_dt(2.0) == 2.0


def test_game_clock_clamps_negative_scale():
    clock = GameClock()
    clock.set_time_scale(-1.0)
    assert clock.time_scale == 0.0
    assert clock.scale_dt(1.0) == 0.0
