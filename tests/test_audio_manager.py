import pygame
import pytest

from audio_manager import AudioManager, get_audio_manager, reset_audio_manager


class DummyChannel:
    def __init__(self) -> None:
        self.volume: float | None = None

    def set_volume(self, value: float) -> None:
        self.volume = value


class DummySound:
    def __init__(self) -> None:
        self.channel = DummyChannel()
        self.last_volume: float | None = None
        self.play_calls = 0

    def set_volume(self, value: float) -> None:
        self.last_volume = value

    def play(self) -> DummyChannel:
        self.play_calls += 1
        return self.channel


def setup_function() -> None:
    pygame.mixer.quit()
    reset_audio_manager()


def teardown_function() -> None:
    reset_audio_manager()


def test_audio_manager_singleton() -> None:
    manager1 = get_audio_manager()
    manager2 = get_audio_manager()
    assert manager1 is manager2


def test_audio_manager_handles_missing_assets() -> None:
    manager = get_audio_manager()
    # Missing assets should not raise during playback attempts.
    manager.play_shot()
    manager.play_asteroid_hit()
    manager.play_bomb()


def test_audio_manager_fallback_when_mixer_fails(monkeypatch) -> None:
    def failing_init() -> None:
        raise pygame.error("init failure")

    monkeypatch.setattr(pygame.mixer, "init", failing_init)
    reset_audio_manager()
    manager = get_audio_manager()
    assert manager.enabled is False
    # Playback should still be a no-op without raising.
    manager.play_shot()


def test_audio_manager_volume_applies_to_playback() -> None:
    manager = get_audio_manager()
    # Replace the registered sound with a dummy so we can inspect volume usage.
    dummy_sound = DummySound()
    manager.enabled = True
    manager._sounds["custom"] = dummy_sound

    manager.set_sfx_volume(0.25)
    manager.play("custom")

    assert dummy_sound.last_volume == 0.25
    assert dummy_sound.channel.volume == 0.25
    assert dummy_sound.play_calls == 1


def test_music_play_and_fade(monkeypatch) -> None:
    class DummyMusicSound:
        def __init__(self, path: str) -> None:
            self.path = path
            self.volume = None

        def set_volume(self, value: float) -> None:
            self.volume = value

    class DummyMusicChannel:
        def __init__(self, index: int, state: dict) -> None:
            self.index = index
            self.state = state
            self.busy = False

        def play(self, sound, loops: int = -1, fade_ms: int = 0) -> None:
            self.state.setdefault("plays", []).append({
                "index": self.index,
                "loops": loops,
                "fade_ms": fade_ms,
                "sound": sound,
            })
            self.busy = True

        def set_volume(self, value: float) -> None:
            self.state.setdefault("volumes", []).append((self.index, value))

        def fadeout(self, ms: int) -> None:
            self.state.setdefault("fadeouts", []).append((self.index, ms))
            self.busy = False

        def stop(self) -> None:
            self.state.setdefault("stops", []).append(self.index)
            self.busy = False

        def get_busy(self) -> bool:
            return self.busy

    state: dict = {
        "num_channels": 0,
        "plays": [],
        "fadeouts": [],
        "volumes": [],
        "stops": [],
    }
    channels: dict[int, DummyMusicChannel] = {}

    monkeypatch.setattr("audio_manager.load_sound", lambda path: DummySound())
    monkeypatch.setattr(pygame.mixer, "get_init", lambda: True)
    monkeypatch.setattr(pygame.mixer, "init", lambda: None)

    def fake_get_num_channels() -> int:
        return state["num_channels"]

    def fake_set_num_channels(value: int) -> None:
        state["num_channels"] = value

    def fake_channel(index: int) -> DummyMusicChannel:
        channel = channels.get(index)
        if channel is None:
            channel = DummyMusicChannel(index, state)
            channels[index] = channel
        if state["num_channels"] < index + 1:
            state["num_channels"] = index + 1
        return channel

    monkeypatch.setattr(pygame.mixer, "get_num_channels", fake_get_num_channels)
    monkeypatch.setattr(pygame.mixer, "set_num_channels", fake_set_num_channels)
    monkeypatch.setattr(pygame.mixer, "Channel", fake_channel)
    monkeypatch.setattr("audio_manager.pygame.mixer.Sound", lambda path: DummyMusicSound(path))

    manager = get_audio_manager()
    music = manager.music
    if not music.enabled or not music.tracks:
        pytest.skip("Music disabled or no tracks available")

    manager.play_level_music(0)
    assert state["plays"], "music should start playback"
    first_play = state["plays"][0]
    assert first_play["loops"] == -1
    assert first_play["fade_ms"] == 1800

    manager.play_level_music(1)
    assert len(state["plays"]) >= 2
    second_play = state["plays"][-1]
    assert second_play["fade_ms"] == 1800
    assert state["fadeouts"] and state["fadeouts"][-1][1] == 1800

    manager.set_music_volume(0.2)
    assert any(abs(volume - 0.2) < 1e-6 for _, volume in state["volumes"])

    manager.fade_out_music(900)
    assert state["fadeouts"][-1][1] == 900

    manager.stop_music()
    assert state["stops"], "channels should stop on shutdown"
