"""
Difficulty Select Screen
[Future Feature] Allows selecting bot difficulty for single player mode
"""

from kivy.uix.label import Label

from screens.base_screen import BaseScreen
from config import SCREENS, BOT_DIFFICULTY


class DifficultySelectScreen(BaseScreen):
    """Difficulty selection screen (placeholder for future implementation)."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Placeholder label
        self.label = Label(
            text='Difficulty Select\n(Coming Soon)',
            font_size=48,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            halign='center'
        )
        self.add_widget(self.label)
    
    def on_enter(self):
        """Called when entering this screen."""
        pass
    
    def on_leave(self):
        """Called when leaving this screen."""
        pass
    
    # TODO: Implement difficulty selection
    # - Display difficulty options: Easy, Medium, Hard
    # - Show description of each difficulty
    # - Use BOT_DIFFICULTY config for settings
    # - Proceed to game with selected difficulty
