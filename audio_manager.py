from __future__ import annotations

import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pygame

from assets import load_sound


_SDL_DUMMY_DRIVER = "dummy"
DEFAULT_SOUND_MAP = {
    "shot": "assets/sounds/Player_Shot.wav",
    "asteroid_hit": "assets/sounds/Asteroid_Hit.wav",
    "bomb": "assets/sounds/Player_Bomb.wav",
    "bomb_pickup": "assets/sounds/Bomb_Pickup.wav",
}
try:
    import numpy as _np  # type: ignore[import-not-found]
    import pygame.sndarray as sndarray  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - numpy may be missing in minimal envs
    _np = None  # type: ignore[assignment]
    sndarray = None  # type: ignore[assignment]

np: Any | None = _np

MUSIC_DIR = Path("assets/music")


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


@dataclass
class SoundPlayConfig:
    volume_jitter: float = 0.0
    pitch_jitter: float = 0.0
    pitch_variants: Tuple[float, ...] = ()


@dataclass
class SoundEntry:
    sound: pygame.mixer.Sound | None
    config: SoundPlayConfig


class MusicPlayer:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled
        self._tracks: List[Path] = []
        self._current_track: Path | None = None
        self._music_volume = 1.0
        self._rng = random.Random()
        self._channel_indices: List[int] = []
        self._active_channel: int | None = None
        self._sound_cache: Dict[Path, pygame.mixer.Sound] = {}
        self._scheduled_tracks: Dict[int, Path] = {}
        if self.enabled:
            self._load_tracks()
            self._prepare_channels()

    def _load_tracks(self) -> None:
        if not MUSIC_DIR.exists():
            return
        self._tracks = [path.resolve() for path in sorted(MUSIC_DIR.glob("*.ogg")) if path.is_file()]

    def _choose_track(self, *, avoid: Path | None = None) -> Path | None:
        if not self._tracks:
            return None
        candidates = list(self._tracks)
        if avoid is not None and len(candidates) > 1:
            candidates = [candidate for candidate in candidates if candidate != avoid]
            if not candidates:
                candidates = list(self._tracks)
        return self._rng.choice(candidates)

    def schedule_preload(self, level_index: int) -> None:
        if not self.enabled or level_index < 0:
            return
        if level_index in self._scheduled_tracks:
            return
        track = self._choose_track(avoid=self._current_track)
        if track is None:
            return
        self._scheduled_tracks[level_index] = track
        self._get_sound(track)

    def _prepare_channels(self) -> None:
        if not self.enabled:
            return
        total = pygame.mixer.get_num_channels()
        if total < 2:
            pygame.mixer.set_num_channels(2)
            total = pygame.mixer.get_num_channels()
        if total < 2:
            self.enabled = False
            return
        if total < 4:
            pygame.mixer.set_num_channels(4)
            total = pygame.mixer.get_num_channels()
        self._channel_indices = [total - 2, total - 1]

    def _channel(self, index: int | None) -> pygame.mixer.Channel | None:
        if index is None:
            return None
        if not pygame.mixer.get_init():
            return None
        return pygame.mixer.Channel(index)

    def _next_channel_index(self) -> int | None:
        if not self._channel_indices:
            return None
        if self._active_channel is None:
            return self._channel_indices[0]
        return next((idx for idx in self._channel_indices if idx != self._active_channel), self._channel_indices[0])

    def _get_sound(self, track: Path) -> pygame.mixer.Sound | None:
        sound = self._sound_cache.get(track)
        if sound is not None:
            return sound
        try:
            sound = pygame.mixer.Sound(track.as_posix())
        except pygame.error:
            return None
        self._sound_cache[track] = sound
        return sound

    def play_random_for_level(
        self,
        level_index: int,
        *,
        fade_out_ms: int = 1800,
        fade_in_ms: int = 1800,
    ) -> None:
        if not self.enabled or not self._tracks:
            return
        track = self._scheduled_tracks.pop(level_index, None)
        if track is None:
            track = self._choose_track(avoid=self._current_track)
        if track is None:
            return
        next_index = self._next_channel_index()
        if next_index is None:
            return
        next_channel = self._channel(next_index)
        if next_channel is None:
            return
        active_channel = self._channel(self._active_channel)
        if active_channel is not None and active_channel.get_busy() and fade_out_ms > 0:
            active_channel.fadeout(fade_out_ms)
        sound = self._get_sound(track)
        if sound is None:
            return
        sound.set_volume(self._music_volume)
        next_channel.play(sound, loops=-1, fade_ms=fade_in_ms)
        next_channel.set_volume(self._music_volume)
        self._active_channel = next_index
        self._current_track = track

    def set_volume(self, volume: float) -> None:
        self._music_volume = _clamp(volume, 0.0, 1.0)
        if not self.enabled:
            return
        for idx in self._channel_indices:
            channel = self._channel(idx)
            if channel is not None:
                channel.set_volume(self._music_volume)

    def fade_out(self, fade_ms: int = 800) -> None:
        if not self.enabled or not pygame.mixer.get_init():
            return
        active_channel = self._channel(self._active_channel)
        if active_channel is not None and active_channel.get_busy():
            active_channel.fadeout(fade_ms)
        self._current_track = None
        self._active_channel = None

    def stop(self) -> None:
        if not self.enabled or not pygame.mixer.get_init():
            return
        for idx in self._channel_indices:
            channel = self._channel(idx)
            if channel is not None:
                channel.stop()
        self._current_track = None
        self._active_channel = None

    @property
    def tracks(self) -> List[Path]:
        return list(self._tracks)

    @property
    def current_track(self) -> Path | None:
        return self._current_track

    @property
    def volume(self) -> float:
        return self._music_volume


class AudioManager:
    """Centralizes sound effect playback and per-level music."""

    def __init__(self) -> None:
        self.enabled = False
        self._sound_entries: Dict[str, SoundEntry] = {}
        self._variant_cache: Dict[Tuple[int, float], pygame.mixer.Sound] = {}
        self._rng = random.Random()
        self.sfx_volume = 1.0
        self._ensure_mixer()
        self._register_defaults()
        self._music = MusicPlayer(self.enabled)
        if self.enabled:
            self._music.set_volume(1.0)
            self._preload_music_tracks()

    def _preload_music_tracks(self) -> None:
        for track in self._music.tracks:
            self._music._get_sound(track)

    def _ensure_mixer(self) -> None:
        if pygame.mixer.get_init():
            self.enabled = True
            return
        try:
            pygame.mixer.init()
            self.enabled = True
            return
        except pygame.error:
            pass
        if os.environ.get("SDL_AUDIODRIVER") != _SDL_DUMMY_DRIVER:
            os.environ.setdefault("SDL_AUDIODRIVER", _SDL_DUMMY_DRIVER)
            try:
                pygame.mixer.init()
                self.enabled = True
                return
            except pygame.error:
                pass
        self.enabled = False

    def _register_defaults(self) -> None:
        for key, path in DEFAULT_SOUND_MAP.items():
            self.register_sound(key, path)
        # Apply subtle jitter defaults for core effects.
        self.configure_sound("shot", volume_jitter=0.12, pitch_jitter=0.06)
        self.configure_sound("asteroid_hit", volume_jitter=0.15, pitch_jitter=0.05)
        self.configure_sound("bomb", volume_jitter=0.08, pitch_jitter=0.0)
        self.configure_sound("bomb_pickup", volume_jitter=0.1, pitch_jitter=0.02)

    def register_sound(self, key: str, path: str) -> None:
        if not self.enabled:
            self._sound_entries[key] = SoundEntry(sound=None, config=SoundPlayConfig())
            return
        try:
            sound = load_sound(path)
        except (FileNotFoundError, pygame.error):
            sound = None
        if sound is not None:
            sound.set_volume(self.sfx_volume)
        self._sound_entries[key] = SoundEntry(sound=sound, config=SoundPlayConfig())

    def set_sfx_volume(self, value: float) -> None:
        self.sfx_volume = _clamp(float(value), 0.0, 1.0)
        for entry in self._sound_entries.values():
            if entry.sound is not None:
                entry.sound.set_volume(self.sfx_volume)

    def configure_sound(
        self,
        key: str,
        *,
        volume_jitter: float | None = None,
        pitch_jitter: float | None = None,
    ) -> None:
        entry = self._sound_entries.get(key)
        if entry is None:
            return
        if volume_jitter is not None:
            entry.config.volume_jitter = max(0.0, float(volume_jitter))
        if pitch_jitter is not None:
            entry.config.pitch_jitter = max(0.0, float(pitch_jitter))
        self._refresh_pitch_variants(entry)

    def _refresh_pitch_variants(self, entry: SoundEntry) -> None:
        jitter = entry.config.pitch_jitter
        if jitter <= 0 or np is None or sndarray is None:
            entry.config.pitch_variants = ()
            return
        base_factors = [1.0 - jitter, 1.0 - jitter * 0.5, 1.0, 1.0 + jitter * 0.5, 1.0 + jitter]
        factors = []
        for factor in base_factors:
            clamped = _clamp(factor, 0.5, 1.5)
            factors.append(round(clamped, 3))
        entry.config.pitch_variants = tuple(sorted(set(factors)))
        if entry.sound is not None:
            for factor in entry.config.pitch_variants:
                if factor != 1.0:
                    self._get_pitch_variant(entry.sound, factor)

    def _random_volume_factor(self, config: SoundPlayConfig) -> float:
        if config.volume_jitter <= 0:
            return 1.0
        jitter = self._rng.uniform(-config.volume_jitter, config.volume_jitter)
        return _clamp(1.0 + jitter, 0.0, 2.0)

    def _random_pitch_factor(self, config: SoundPlayConfig) -> float:
        if not config.pitch_variants:
            return 1.0
        return self._rng.choice(config.pitch_variants)

    def _get_pitch_variant(
        self,
        base_sound: pygame.mixer.Sound,
        pitch_factor: float,
    ) -> pygame.mixer.Sound | None:
        if np is None or sndarray is None or pitch_factor == 1.0:
            return base_sound
        cache_key = (id(base_sound), round(pitch_factor, 3))
        cached = self._variant_cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            samples = sndarray.array(base_sound)
        except Exception:
            return base_sound
        if samples.size == 0:
            return base_sound
        source_length = samples.shape[0]
        new_length = max(1, int(source_length / pitch_factor))
        source_indices = np.arange(source_length)
        target_indices = np.linspace(0, source_length - 1, new_length)
        if samples.ndim == 1:
            resampled = np.interp(target_indices, source_indices, samples).astype(samples.dtype, copy=False)
        else:
            channels = []
            for channel_index in range(samples.shape[1]):
                channel_data = np.interp(
                    target_indices,
                    source_indices,
                    samples[:, channel_index],
                )
                channels.append(channel_data)
            resampled = np.stack(channels, axis=1)
            resampled = resampled.astype(samples.dtype, copy=False)
        if np.issubdtype(samples.dtype, np.integer):
            info = np.iinfo(samples.dtype)
            resampled = np.clip(resampled, info.min, info.max).astype(samples.dtype)
        else:
            resampled = resampled.astype(samples.dtype)
        try:
            new_sound = sndarray.make_sound(np.ascontiguousarray(resampled))
        except Exception:
            return base_sound
        new_sound.set_volume(self.sfx_volume)
        self._variant_cache[cache_key] = new_sound
        return new_sound

    def play(self, key: str) -> None:
        entry = self._sound_entries.get(key)
        if not self.enabled or entry is None or entry.sound is None:
            return
        sound_to_play = entry.sound
        pitch_factor = self._random_pitch_factor(entry.config)
        if pitch_factor != 1.0:
            variant = self._get_pitch_variant(entry.sound, pitch_factor)
            if variant is not None:
                sound_to_play = variant
        channel = sound_to_play.play()
        if channel is not None:
            volume_factor = self._random_volume_factor(entry.config)
            channel.set_volume(_clamp(self.sfx_volume * volume_factor, 0.0, 1.0))

    def play_shot(self) -> None:
        self.play("shot")

    def play_asteroid_hit(self) -> None:
        self.play("asteroid_hit")

    def play_bomb(self) -> None:
        self.play("bomb")

    def play_bomb_pickup(self) -> None:
        self.play("bomb_pickup")

    def play_level_music(self, level_index: int, *, transition_ms: int | None = None) -> None:
        duration = 1800 if transition_ms is None else max(0, int(transition_ms))
        self._music.play_random_for_level(level_index, fade_out_ms=duration, fade_in_ms=duration)
        self._music.schedule_preload(level_index + 1)

    def preload_level_music(self, level_index: int) -> None:
        self._music.schedule_preload(level_index)

    def set_music_volume(self, value: float) -> None:
        self._music.set_volume(value)

    def fade_out_music(self, fade_ms: int = 800) -> None:
        self._music.fade_out(fade_ms)

    def stop_music(self) -> None:
        self._music.stop()

    @property
    def music(self) -> MusicPlayer:
        return self._music


_audio_manager: AudioManager | None = None


def get_audio_manager() -> AudioManager:
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager


def reset_audio_manager() -> None:
    global _audio_manager
    if _audio_manager is not None:
        if pygame.mixer.get_init():
            _audio_manager.stop_music()
    _audio_manager = None
