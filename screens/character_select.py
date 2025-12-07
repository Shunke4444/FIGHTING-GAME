"""
Character Select Screen
[Future Feature] Allows players to select their fighters
"""

from kivy.uix.label import Label

from screens.base_screen import BaseScreen
from config import SCREENS


class CharacterSelectScreen(BaseScreen):
    """Character selection screen (placeholder for future implementation)."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Placeholder label
        self.label = Label(
            text='Character Select\n(Coming Soon)',
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
    
    # TODO: Implement character selection
    # - Display available characters with preview sprites
    # - Allow P1 and P2 to select independently
    # - Show selected character stats
    # - Proceed to game or difficulty select
