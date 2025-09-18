import pygame

from fx_manager import FXManager

class DummyTarget:
    def __init__(self, position: pygame.Vector2) -> None:
        self.position = pygame.Vector2(position)


def test_fx_manager_particles_and_flash_decay():
    manager = FXManager()
    surface = pygame.Surface((200, 200), pygame.SRCALPHA)

    manager.spawn_asteroid_explosion(pygame.Vector2(100, 100), 30)
    manager.trigger_flash((255, 0, 0), duration=0.2, alpha=180)

    assert manager.offset() == (0, 0)

    manager.update(0.1, 0.1)
    manager.draw_world(surface)
    manager.draw_overlay(surface)

    manager.update(0.2, 0.2)
    manager.draw_overlay(surface)

    manager.update(0.5, 0.5)
    manager.draw_world(surface)
    manager.draw_overlay(surface)

    assert not manager._flashes
    assert not manager._particles


def test_fx_manager_bomb_activation_and_pickup_fx():
    manager = FXManager()
    surface = pygame.Surface((200, 200), pygame.SRCALPHA)
    dummy = DummyTarget(pygame.Vector2(55, 55))

    manager.spawn_bomb_activation(pygame.Vector2(50, 50))
    manager.spawn_pickup_glow(pygame.Vector2(60, 60))
    manager.spawn_powerup_trail(dummy, (220, 60, 60))
    manager.spawn_level_transition()
    manager.shake(0.5, 10.0)

    manager.update(0.3, 0.3)
    manager.draw_world(surface)
    manager.draw_overlay(surface)

    # After more time effects should clear and shake should settle.
    dummy.position = pygame.Vector2(75, 70)
    manager.update(0.25, 0.25)
    manager.draw_world(surface)
    manager.draw_overlay(surface)
    manager.update(1.0, 1.0)
    manager.draw_world(surface)

    offset = manager.offset()
    assert isinstance(offset, tuple)
    assert len(offset) == 2
    assert not manager._powerup_effects


def test_fx_fireworks_cleanup() -> None:
    manager = FXManager()

    manager.start_fireworks(duration=0.4, interval=0.05)
    manager.update(0.05)
    assert manager._particles, "fireworks should spawn particles"

    manager.update(0.6)
    manager.update(1.2)

    assert not manager._particles
    assert manager._fireworks_timer == 0.0
