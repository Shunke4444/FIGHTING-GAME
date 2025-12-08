"""
Game Configuration and Constants
All game settings, sprite configurations, and constants are defined here.
"""

from kivy.utils import platform
from kivy.core.window import Window

# =============================================================================
# WINDOW SETTINGS
# =============================================================================

# Set window size for desktop testing only (mobile will use fullscreen automatically)
if platform not in ('android', 'ios'):
    Window.size = (1000, 600)

# =============================================================================
# GAME SETTINGS
# =============================================================================

# Frame rate
FPS = 60

# Ground level (from bottom of screen)
GROUND_Y = 110

# Fighter settings
FIGHTER_SPEED = 10
GRAVITY = 2
MAX_JUMPS = 2
JUMP_VELOCITY = 30

# Attack damage values
ATTACK_DAMAGE = {
    1: 8,   # Light attack
    2: 12,  # Medium attack
    3: 18,  # Heavy attack (combo)
}

# Attack range
ATTACK_RANGE = 80

# Cooldowns (in frames)
HIT_COOLDOWN = 45      # Invincibility after getting hit
ATTACK_COOLDOWN = 25   # Delay between attacks
DODGE_COOLDOWN = 60    # Delay between dodges (1 second at 60 FPS)

# Dodge settings
DODGE_DISTANCE = 150   # How far the dodge moves
DODGE_DURATION = 8     # How many frames the dodge lasts

# Animation speed (frames per animation frame)
FRAMES_PER_ANIMATION = 5

# =============================================================================
# SPRITE CONFIGURATIONS
# =============================================================================

SPRITE_CONFIG = {
    'fantasy_warrior': {
        'scale_width': 250,
        'scale_height': 250,
        'visual_y_pull': 35,
        'death_y_adj': 20,
        'animations': {
            'Idle': 10,
            'Run': 8,
            'Jump': 3,
            'Attack1': 7,
            'Attack2': 7,
            'Attack3': 8,
            'Take hit': 3,
            'Death': 7
        }
    },
    'knight': {
        'scale_width': 250,
        'scale_height': 170,
        'visual_y_pull': -60,
        'death_y_adj': 10,
        'animations': {
            'Idle': 10,
            'Run': 10,
            'Jump': 3,
            'Attack1': 4,
            'Attack2': 6,
            'Attack3': 10,
            'hit': 1,
            'Death': 10
        }
    }
}

# =============================================================================
# UI SETTINGS
# =============================================================================

# Health bar
HEALTH_BAR_WIDTH = 300
HEALTH_BAR_HEIGHT = 30
HEALTH_BAR_OFFSET_Y = 50  # From top of screen

# Touch button settings
BUTTON_SIZE = (80, 80)
BUTTON_OPACITY = 0.7

# Button colors (RGBA)
COLORS = {
    'p1_movement': (0.3, 0.3, 0.8, BUTTON_OPACITY),
    'p1_attack': (0.8, 0.3, 0.3, BUTTON_OPACITY),
    'p2_movement': (0.8, 0.6, 0.3, BUTTON_OPACITY),
    'p2_attack': (0.8, 0.5, 0.3, BUTTON_OPACITY),
    'jump': (0.3, 0.8, 0.3, BUTTON_OPACITY),
    'pause': (0.5, 0.5, 0.5, BUTTON_OPACITY),
}

# =============================================================================
# SCREEN NAMES
# =============================================================================

SCREENS = {
    'START': 'start',
    'CHARACTER_SELECT': 'character_select',
    'DIFFICULTY_SELECT': 'difficulty_select',
    'GAME': 'game',
    'PAUSE': 'pause',
    'GAME_OVER': 'game_over',
    'SETTINGS': 'settings',
    'CONTROL_LAYOUT': 'control_layout',
}

# =============================================================================
# ASSET PATHS
# =============================================================================

ASSET_PATHS = {
    'backgrounds': 'assets/images/backgrounds/',
    'characters': 'assets/images/characters/',
}

# Default background
DEFAULT_BACKGROUND = 'FOREST.png'

# =============================================================================
# BOT DIFFICULTY SETTINGS (Future feature)
# =============================================================================

BOT_DIFFICULTY = {
    'easy': {
        'reaction_time': 30,  # frames before reacting
        'attack_chance': 0.3,
        'block_chance': 0.1,
    },
    'medium': {
        'reaction_time': 15,
        'attack_chance': 0.5,
        'block_chance': 0.3,
    },
    'hard': {
        'reaction_time': 5,
        'attack_chance': 0.7,
        'block_chance': 0.5,
    },
    'nightmare': {
        'reaction_time': 2,
        'attack_chance': 0.85,
        'block_chance': 0.7,
    },
}
