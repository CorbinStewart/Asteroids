import os

import pygame
import pytest

from audio_manager import (
    AudioManager,
    get_audio_manager,
    reset_audio_manager,
    np as audio_np,
)


class DummyChannel:
    def __init__(self) -> None:
        self.volume: float | None = None

    def set_volume(self, *values: float) -> None:
        if not values:
            return
        # pygame.Channel.set_volume accepts 1 or 2 values; store the first.
        self.volume = values[0]


class DummySound:
    def __init__(self) -> None:
        self.channel = DummyChannel()
        self.last_volume: float | None = None
        self.play_calls = 0

    def set_volume(self, value: float) -> None:
        self.last_volume = value

    def play(self, loops: int = 0, maxtime: int = 0, fade_ms: int = 0) -> DummyChannel:
        self.play_calls += 1
        return self.channel

    def get_volume(self) -> float:
        return self.last_volume if self.last_volume is not None else 1.0


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
    manager.configure_sound("shot", volume_jitter=0.0, pitch_jitter=0.0)
    entry = manager._sound_entries.get("shot")
    assert entry is not None
    dummy_sound = DummySound()
    entry.sound = dummy_sound
    entry.config.volume_jitter = 0.0
    entry.config.pitch_jitter = 0.0
    entry.config.pitch_variants = ()
    manager.enabled = True
    manager.set_sfx_volume(0.25)

    # Ensure playback uses deterministic factors.
    manager.configure_sound("shot", volume_jitter=0.0, pitch_jitter=0.0)
    manager.play_shot()

    assert dummy_sound.last_volume == 0.25
    assert dummy_sound.channel.volume == 0.25
    assert dummy_sound.play_calls == 1


def test_volume_jitter_adjusts_channel_volume(monkeypatch) -> None:
    manager = get_audio_manager()
    manager.configure_sound("asteroid_hit", volume_jitter=0.2, pitch_jitter=0.0)
    entry = manager._sound_entries.get("asteroid_hit")
    assert entry is not None
    dummy_sound = DummySound()
    entry.sound = dummy_sound
    entry.config.volume_jitter = 0.2
    entry.config.pitch_jitter = 0.0
    manager.enabled = True
    manager.set_sfx_volume(0.5)

    monkeypatch.setattr(manager, "_random_volume_factor", lambda config: 1.2)
    monkeypatch.setattr(manager, "_random_pitch_factor", lambda config: 1.0)

    manager.play_asteroid_hit()

    assert dummy_sound.channel.volume is not None
    assert pytest.approx(0.6, rel=1e-6) == dummy_sound.channel.volume


def test_music_play_and_fade(monkeypatch) -> None:
    class DummyMusicSound:
        def __init__(self, path: str) -> None:
            self.path = path
            self.volume = None
            self.volume_calls: list[float] = []

        def set_volume(self, value: float) -> None:
            self.volume = value
            self.volume_calls.append(value)

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

    manager.set_music_volume(0.0)
    assert any(abs(volume) < 1e-6 for _, volume in state["volumes"])

    manager.play_level_music(2)
    third_play = state["plays"][-1]
    assert third_play["fade_ms"] == 0, "Muted playback should skip fade"
    assert state["volumes"][-1][1] == 0.0

    manager.set_music_volume(0.45)
    assert state["volumes"][-1][1] == pytest.approx(0.45, rel=1e-6)

    manager.fade_out_music(900)
    assert state["fadeouts"][-1][1] == 900

    manager.stop_music()
    assert state["stops"], "channels should stop on shutdown"

    # All cached sounds should keep unity gain so channel volume drives loudness.
    played_sounds = [entry["sound"] for entry in state["plays"]]
    assert played_sounds
    for sound in played_sounds:
        assert sound.volume_calls, "Expected set_volume to be called on music sound"
        for volume in sound.volume_calls:
            assert pytest.approx(1.0, rel=1e-6) == volume


def test_pitch_variants_precomputed() -> None:
    manager = get_audio_manager()
    entry = manager._sound_entries.get("shot")
    if entry is None or entry.sound is None or audio_np is None:
        pytest.skip("Pitch resampling unavailable on this platform")

    manager.configure_sound("shot", pitch_jitter=0.04)
    variants = entry.config.pitch_variants
    assert variants
    off_unity = [factor for factor in variants if factor != 1.0]
    assert off_unity, "Expected at least one non-unity pitch variant"
    cache_keys = {key for key in manager._variant_cache if key[0] == id(entry.sound)}
    assert cache_keys, "Expected cached pitch variants"
    for factor in off_unity:
        rounded = round(factor, 3)
        assert (id(entry.sound), rounded) in cache_keys


def test_audio_manager_promotes_dummy_driver_when_device_missing(monkeypatch) -> None:
    call_order: list[str | None] = []

    def fake_get_init() -> bool:
        return len(call_order) >= 2

    def fake_init() -> None:
        call_order.append(os.environ.get("SDL_AUDIODRIVER"))
        if len(call_order) == 1:
            raise pygame.error("No audio device")

    class DummyMusicChannel:
        def __init__(self) -> None:
            self.volume = 1.0

        def set_volume(self, value: float) -> None:
            self.volume = value

        def get_busy(self) -> bool:
            return False

        def fadeout(self, ms: int) -> None:
            pass

        def stop(self) -> None:
            pass

        def play(self, sound, loops: int = -1, fade_ms: int = 0) -> None:
            pass

    monkeypatch.delenv("SDL_AUDIODRIVER", raising=False)
    monkeypatch.setattr(pygame.mixer, "get_init", fake_get_init)
    monkeypatch.setattr(pygame.mixer, "init", fake_init)
    monkeypatch.setattr(pygame.mixer, "get_num_channels", lambda: 4)
    monkeypatch.setattr(pygame.mixer, "set_num_channels", lambda value: None)
    monkeypatch.setattr(pygame.mixer, "Channel", lambda index: DummyMusicChannel())
    monkeypatch.setattr("audio_manager.load_sound", lambda path: DummySound())

    manager = get_audio_manager()

    assert manager.enabled is True
    assert len(call_order) >= 2
    assert call_order[0] != "dummy"
    assert call_order[-1] == "dummy"
    assert os.environ.get("SDL_AUDIODRIVER") == "dummy"
