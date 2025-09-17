from profile_manager import ProfileManager, DEFAULT_PROFILE


def test_record_milestones_append_values(tmp_path):
    path = tmp_path / "profile.json"
    manager = ProfileManager(path=path)
    manager.record_milestones(
        asteroids_destroyed=5,
        bombs_used=2,
        pickups_collected=3,
        time_survived=12.5,
    )
    manager.record_milestones(
        asteroids_destroyed=2,
        bombs_used=1,
        pickups_collected=0,
        time_survived=3.5,
    )

    milestones = manager.data["scores"]["milestones"]
    assert milestones["total_asteroids_destroyed"] == 7
    assert milestones["total_bombs_used"] == 3
    assert milestones["total_pickups_collected"] == 3
    assert milestones["total_time_survived"] == 16.0


def test_save_load_milestones(tmp_path):
    path = tmp_path / "profile.json"
    manager = ProfileManager(path=path)
    manager.record_milestones(
        asteroids_destroyed=1,
        bombs_used=1,
        pickups_collected=1,
        time_survived=10.0,
    )
    manager.save()

    reloaded = ProfileManager(path=path)
    reloaded.load()
    milestones = reloaded.data["scores"]["milestones"]
    assert milestones["total_time_survived"] == 10.0
