from profile_manager import ProfileManager


def test_update_settings_clamps_and_truncates(tmp_path):
    path = tmp_path / "profile.json"
    manager = ProfileManager(path=path)

    manager.update_settings(music_volume=1.5, sfx_volume=-0.5, screen_shake=0.75, player_name="Commander Vector")

    settings = manager.settings()
    assert settings["music_volume"] == 1.0
    assert settings["sfx_volume"] == 0.0
    assert settings["screen_shake"] == 0.75
    assert settings["player_name"] == "Commander"


def test_settings_persist_across_save(tmp_path):
    path = tmp_path / "profile.json"
    manager = ProfileManager(path=path)
    manager.update_settings(music_volume=0.25, sfx_volume=0.5, screen_shake=0.1, player_name="Ace")
    manager.save()

    reloaded = ProfileManager(path=path)
    reloaded.load()
    settings = reloaded.settings()
    assert settings["music_volume"] == 0.25
    assert settings["sfx_volume"] == 0.5
    assert settings["screen_shake"] == 0.1
    assert settings["player_name"] == "Ace"
