SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE = 0.8  # seconds
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS

PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN = 0.3

SHOT_RADIUS = 5
SHOT_LIFETIME = 3.0

STATUS_BAR_HEIGHT = 96
STATUS_BAR_TOP_COLOR = (13, 16, 32)
STATUS_BAR_BOTTOM_COLOR = (5, 6, 13)

PLAYER_START_LIVES = 3
PLAYER_RESPAWN_INVULNERABILITY = 5.0
LIFE_ICON_SIZE = 12
LIFE_ICON_SPACING = 28
LIFE_ICON_FLICKER_DURATION = 0.7
LIFE_ICON_FLICKER_INTERVAL = 0.12
LIFE_ICON_FLICKER_COLOR = (160, 32, 32)
PLAYER_SHIELD_RADIUS_PADDING = 20
PLAYER_INVULNERABILITY_FADE_WINDOW = 2.0
HUD_FONT_SIZE = 24
SUBHEADER_FONT_SIZE = 16
HEADER_FONT_SIZE = 48
ORBITRON_FONT_PATH = "assets/fonts/Orbitron-Regular.ttf"
ORBITRON_SEMIBOLD_FONT_PATH = "assets/fonts/Orbitron-SemiBold.ttf"
LEVEL_MESSAGE_DURATION = 2.0

LEVEL_DEFINITIONS = [
    {"spawn_total": 10, "max_active": 10, "speed_multiplier": 1.0},
    {"spawn_total": 14, "max_active": 12, "speed_multiplier": 1.0},
    {"spawn_total": 20, "max_active": 15, "speed_multiplier": 1.1},
    {"spawn_total": 26, "max_active": 18, "speed_multiplier": 1.15},
    {"spawn_total": 30, "max_active": 22, "speed_multiplier": 1.2},
    {"spawn_total": 35, "max_active": 25, "speed_multiplier": 1.35},
    {"spawn_total": 35, "max_active": 25, "speed_multiplier": 1.5},
    {"spawn_total": 35, "max_active": 25, "speed_multiplier": 1.65},
    {"spawn_total": 35, "max_active": 25, "speed_multiplier": 1.8},
    {"spawn_total": 35, "max_active": 25, "speed_multiplier": 2.0},
]

ASTEROID_SCORE_LARGE = 1
ASTEROID_SCORE_MEDIUM = 3
ASTEROID_SCORE_SMALL = 5
LEVEL_CLEAR_BONUS = 1000
