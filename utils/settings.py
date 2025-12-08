"""
Settings Manager
Handles loading and saving game settings including control layouts
"""

import copy
import json
import os
from kivy.utils import platform


def get_settings_path():
    """Get the path to the settings file based on platform."""
    if platform == 'android':
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), 'settings.json')
    else:
        # For desktop, use the game directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'settings.json')


# Default control layout (relative positions as percentages of screen)
# Each button has x, y position and optional individual scale/opacity
DEFAULT_CONTROLS = {
    'left': {'x': 0.03, 'y': 0.18, 'scale': 1.0, 'opacity': 0.8},
    'right': {'x': 0.14, 'y': 0.18, 'scale': 1.0, 'opacity': 0.8},
    'atk1': {'x': 0.75, 'y': 0.03, 'scale': 1.0, 'opacity': 0.8},
    'atk2': {'x': 0.87, 'y': 0.03, 'scale': 1.0, 'opacity': 0.8},
    'jump': {'x': 0.87, 'y': 0.18, 'scale': 1.0, 'opacity': 0.8},
    'dodge': {'x': 0.75, 'y': 0.18, 'scale': 1.0, 'opacity': 0.8},
    'button_scale': 1.0,  # Global scale (kept for backward compatibility)
    'button_opacity': 0.8,  # Global opacity (kept for backward compatibility)
}

# Default settings
DEFAULT_SETTINGS = {
    'controls': DEFAULT_CONTROLS.copy(),
    'presets': {},  # User-saved presets
    'active_preset': None,
    'audio': {
        'music_volume': 0.15,
        'sfx_volume': 0.5,
    },
}


class SettingsManager:
    """Manages game settings persistence."""
    
    _instance = None
    _settings = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = SettingsManager()
        return cls._instance
    
    def __init__(self):
        """Initialize settings manager."""
        self._settings = None
        self.load()
    
    def load(self):
        """Load settings from file."""
        try:
            settings_path = get_settings_path()
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    self._settings = json.load(f)
                # Ensure all required keys exist
                self._validate_settings()
            else:
                self._settings = copy.deepcopy(DEFAULT_SETTINGS)
        except Exception as e:
            print(f"Error loading settings: {e}")
            self._settings = copy.deepcopy(DEFAULT_SETTINGS)
    
    def _validate_settings(self):
        """Ensure all required settings exist."""
        if 'controls' not in self._settings:
            self._settings['controls'] = copy.deepcopy(DEFAULT_CONTROLS)
        else:
            # Ensure all control keys exist
            for key, value in DEFAULT_CONTROLS.items():
                if key not in self._settings['controls']:
                    if isinstance(value, dict):
                        self._settings['controls'][key] = copy.deepcopy(value)
                    else:
                        self._settings['controls'][key] = value
        
        if 'presets' not in self._settings:
            self._settings['presets'] = {}
        
        if 'active_preset' not in self._settings:
            self._settings['active_preset'] = None
        
        # Validate audio settings
        if 'audio' not in self._settings:
            self._settings['audio'] = {
                'music_volume': 0.15,
                'sfx_volume': 0.5,
            }
        else:
            if 'music_volume' not in self._settings['audio']:
                self._settings['audio']['music_volume'] = 0.15
            if 'sfx_volume' not in self._settings['audio']:
                self._settings['audio']['sfx_volume'] = 0.5
    
    def save(self):
        """Save settings to file."""
        try:
            settings_path = get_settings_path()
            with open(settings_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def reload(self):
        """Reload settings from file."""
        self.load()
    
    def get_controls(self):
        """Get current control layout."""
        return self._settings.get('controls', DEFAULT_CONTROLS.copy())
    
    def set_control_position(self, control_name, x_percent, y_percent):
        """Set a control's position (as percentage of screen)."""
        if control_name in self._settings['controls']:
            if isinstance(self._settings['controls'][control_name], dict):
                self._settings['controls'][control_name]['x'] = x_percent
                self._settings['controls'][control_name]['y'] = y_percent
    
    def get_button_scale(self):
        """Get button scale factor."""
        return self._settings['controls'].get('button_scale', 1.0)
    
    def set_button_scale(self, scale):
        """Set button scale factor (0.5 to 1.5)."""
        self._settings['controls']['button_scale'] = max(0.5, min(1.5, scale))
    
    def get_button_opacity(self):
        """Get button opacity."""
        return self._settings['controls'].get('button_opacity', 0.8)
    
    def set_button_opacity(self, opacity):
        """Set button opacity (0.3 to 1.0)."""
        self._settings['controls']['button_opacity'] = max(0.3, min(1.0, opacity))
    
    def get_individual_button_scale(self, control_name):
        """Get individual button scale factor."""
        if control_name in self._settings['controls']:
            ctrl = self._settings['controls'][control_name]
            if isinstance(ctrl, dict):
                return ctrl.get('scale', self.get_button_scale())
        return self.get_button_scale()
    
    def set_individual_button_scale(self, control_name, scale):
        """Set individual button scale factor (0.5 to 1.5)."""
        if control_name in self._settings['controls']:
            ctrl = self._settings['controls'][control_name]
            if isinstance(ctrl, dict):
                ctrl['scale'] = max(0.5, min(1.5, scale))
    
    def get_individual_button_opacity(self, control_name):
        """Get individual button opacity."""
        if control_name in self._settings['controls']:
            ctrl = self._settings['controls'][control_name]
            if isinstance(ctrl, dict):
                return ctrl.get('opacity', self.get_button_opacity())
        return self.get_button_opacity()
    
    def set_individual_button_opacity(self, control_name, opacity):
        """Set individual button opacity (0.3 to 1.0)."""
        if control_name in self._settings['controls']:
            ctrl = self._settings['controls'][control_name]
            if isinstance(ctrl, dict):
                ctrl['opacity'] = max(0.3, min(1.0, opacity))
    
    def save_preset(self, preset_name):
        """Save current controls as a preset."""
        self._settings['presets'][preset_name] = {
            'left': self._settings['controls']['left'].copy(),
            'right': self._settings['controls']['right'].copy(),
            'atk1': self._settings['controls']['atk1'].copy(),
            'atk2': self._settings['controls']['atk2'].copy(),
            'jump': self._settings['controls']['jump'].copy(),
            'dodge': self._settings['controls']['dodge'].copy(),
            'button_scale': self._settings['controls']['button_scale'],
            'button_opacity': self._settings['controls']['button_opacity'],
        }
        self._settings['active_preset'] = preset_name
        self.save()
    
    def load_preset(self, preset_name):
        """Load a saved preset."""
        if preset_name in self._settings['presets']:
            preset = self._settings['presets'][preset_name]
            for key, value in preset.items():
                if isinstance(value, dict):
                    self._settings['controls'][key] = value.copy()
                else:
                    self._settings['controls'][key] = value
            self._settings['active_preset'] = preset_name
            self.save()
            return True
        return False
    
    def delete_preset(self, preset_name):
        """Delete a saved preset."""
        if preset_name in self._settings['presets']:
            del self._settings['presets'][preset_name]
            if self._settings['active_preset'] == preset_name:
                self._settings['active_preset'] = None
            self.save()
            return True
        return False
    
    def get_presets(self):
        """Get list of saved preset names."""
        return list(self._settings['presets'].keys())
    
    def reset_to_default(self):
        """Reset controls to default layout."""
        self._settings['controls'] = copy.deepcopy(DEFAULT_CONTROLS)
        self._settings['active_preset'] = None
        self.save()
    
    def get_music_volume(self):
        """Get music volume (0.0 to 1.0)."""
        return self._settings.get('audio', {}).get('music_volume', 0.15)
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)."""
        if 'audio' not in self._settings:
            self._settings['audio'] = {}
        self._settings['audio']['music_volume'] = max(0.0, min(1.0, volume))
        self.save()
    
    def get_sfx_volume(self):
        """Get sound effects volume (0.0 to 1.0)."""
        return self._settings.get('audio', {}).get('sfx_volume', 0.5)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)."""
        if 'audio' not in self._settings:
            self._settings['audio'] = {}
        self._settings['audio']['sfx_volume'] = max(0.0, min(1.0, volume))
        self.save()
