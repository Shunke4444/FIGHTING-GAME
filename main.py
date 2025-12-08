"""
Fighting Game - Mobile Version
Main entry point for the application

This game is built with Kivy and can be compiled to APK using Buildozer.

Project Structure:
- main.py          : This file - app entry point and screen management
- config.py        : Game settings and constants
- screens/         : All game screens (start, game, pause, etc.)
- components/      : Reusable game components (fighter, controls, health bar)
- utils/           : Utility functions
- assets/          : Images, sounds, and other assets
"""

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

# Import config first to set up window
import config

from screens import (
    StartScreen,
    GameScreen, 
    PauseScreen,
    CharacterSelectScreen,
    DifficultySelectScreen,
    SettingsScreen,
    ControlLayoutScreen,
)
from config import SCREENS


class FightingGameApp(App):
    """Main application class that manages screens."""
    
    def build(self):
        """Build the application."""
        # Create root layout
        self.root_layout = FloatLayout()
        
        # Dictionary to store screen instances
        self.screens = {}
        
        # Create all screens
        self._create_screens()
        
        # Start with the start screen
        self.current_screen = None
        self.switch_screen(SCREENS['START'])
        
        # Bind to window resize
        Window.bind(size=self.on_window_resize)
        
        return self.root_layout
    
    def _create_screens(self):
        """Create all screen instances."""
        self.screens[SCREENS['START']] = StartScreen(self)
        self.screens[SCREENS['GAME']] = GameScreen(self)
        self.screens[SCREENS['PAUSE']] = PauseScreen(self)
        self.screens[SCREENS['CHARACTER_SELECT']] = CharacterSelectScreen(self)
        self.screens[SCREENS['DIFFICULTY_SELECT']] = DifficultySelectScreen(self)
        self.screens[SCREENS['SETTINGS']] = SettingsScreen(self)
        self.screens[SCREENS['CONTROL_LAYOUT']] = ControlLayoutScreen(self)
    
    def switch_screen(self, screen_name):
        """Switch to a different screen."""
        # Leave current screen
        if self.current_screen:
            self.current_screen.on_leave()
            self.root_layout.remove_widget(self.current_screen)
        
        # Get new screen
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]
            self.root_layout.add_widget(self.current_screen)
            self.current_screen.on_enter()
        else:
            print(f"Warning: Screen '{screen_name}' not found")
    
    def on_window_resize(self, window, size):
        """Handle window resize events."""
        # Propagate to current screen if needed
        if self.current_screen:
            self.current_screen.on_window_resize(window, size)
    
    def on_pause(self):
        """Called when app is paused (mobile)."""
        return True
    
    def on_resume(self):
        """Called when app resumes (mobile)."""
        pass


if __name__ == '__main__':
    FightingGameApp().run()
