"""
Utility functions and helpers for the game.
"""

import os


def get_base_path():
    """Get the base path of the application."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_asset_path(*path_parts):
    """Get the full path to an asset file."""
    return os.path.join(get_base_path(), *path_parts)


def clamp(value, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def lerp(start, end, t):
    """Linear interpolation between two values."""
    return start + (end - start) * t
