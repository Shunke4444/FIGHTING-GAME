"""
Pause Screen
Overlay shown when the game is paused
"""

import os
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color

from screens.base_screen import BaseScreen
from config import SCREENS


class PauseScreen(BaseScreen):
    """Pause screen overlay."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Load pixel fonts
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pixelmax_font = os.path.join(base_path, 'assets/fonts/Pixelmax-Regular.otf')
        self.pixelade_font = os.path.join(base_path, 'assets/fonts/PIXELADE.TTF')
        
        # Semi-transparent background
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.bg_rect = Rectangle(pos=(0, 0), size=self.size)
        
        # Bind size to update rectangle
        self.bind(size=self._update_bg)
        
        # Pause title
        self.title_label = Label(
            text='PAUSED',
            font_size=64,
            font_name=self.pixelmax_font,
            bold=True,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            size_hint=(None, None)
        )
        self.add_widget(self.title_label)
        
        # Resume button
        self.resume_btn = Button(
            text='Resume',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color=(0.3, 0.7, 0.3, 1),
            font_size=28,
            font_name=self.pixelade_font
        )
        self.resume_btn.bind(on_press=self.on_resume)
        self.add_widget(self.resume_btn)
        
        # Restart button
        self.restart_btn = Button(
            text='Restart',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.7, 0.7, 0.3, 1),
            font_size=28,
            font_name=self.pixelade_font
        )
        self.restart_btn.bind(on_press=self.on_restart)
        self.add_widget(self.restart_btn)
        
        # Change Difficulty button
        self.difficulty_btn = Button(
            text='Change Difficulty',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            background_color=(0.5, 0.3, 0.7, 1),
            font_size=24,
            font_name=self.pixelade_font
        )
        self.difficulty_btn.bind(on_press=self.on_change_difficulty)
        self.add_widget(self.difficulty_btn)
        
        # Quit button
        self.quit_btn = Button(
            text='Main Menu',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            background_color=(0.7, 0.3, 0.3, 1),
            font_size=28,
            font_name=self.pixelade_font
        )
        self.quit_btn.bind(on_press=self.on_quit)
        self.add_widget(self.quit_btn)
    
    def _update_bg(self, instance, value):
        """Update background rectangle size."""
        self.bg_rect.size = self.size
    
    def on_resume(self, instance):
        """Resume the game."""
        self.app.switch_screen(SCREENS['GAME'])
    
    def on_restart(self, instance):
        """Restart the game."""
        # Reset the game state
        if hasattr(self.app, 'screens') and SCREENS['GAME'] in self.app.screens:
            self.app.screens[SCREENS['GAME']].reset_game()
        self.app.switch_screen(SCREENS['GAME'])
    
    def on_quit(self, instance):
        """Return to main menu."""
        # Reset the game state and stop music
        if hasattr(self.app, 'screens') and SCREENS['GAME'] in self.app.screens:
            self.app.screens[SCREENS['GAME']].reset_game()
            self.app.screens[SCREENS['GAME']].stop_music()
        self.app.switch_screen(SCREENS['START'])
    
    def on_change_difficulty(self, instance):
        """Go to difficulty select screen."""
        self.app.switch_screen(SCREENS['DIFFICULTY_SELECT'])
