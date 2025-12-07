"""
Pause Screen
Overlay shown when the game is paused
"""

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color

from screens.base_screen import BaseScreen
from config import SCREENS


class PauseScreen(BaseScreen):
    """Pause screen overlay."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
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
            font_size=28
        )
        self.resume_btn.bind(on_press=self.on_resume)
        self.add_widget(self.resume_btn)
        
        # Restart button
        self.restart_btn = Button(
            text='Restart',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5, 'center_y': 0.35},
            background_color=(0.7, 0.7, 0.3, 1),
            font_size=28
        )
        self.restart_btn.bind(on_press=self.on_restart)
        self.add_widget(self.restart_btn)
        
        # Quit button
        self.quit_btn = Button(
            text='Main Menu',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_color=(0.7, 0.3, 0.3, 1),
            font_size=28
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
        # Reset the game state
        if hasattr(self.app, 'screens') and SCREENS['GAME'] in self.app.screens:
            self.app.screens[SCREENS['GAME']].reset_game()
        self.app.switch_screen(SCREENS['START'])
