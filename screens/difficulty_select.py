"""
Difficulty Select Screen
Allows selecting bot difficulty for single player mode
"""

import os
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from screens.base_screen import BaseScreen
from config import SCREENS


class DifficultySelectScreen(BaseScreen):
    """Difficulty selection screen."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Load pixel fonts
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pixelmax_font = os.path.join(base_path, 'assets/fonts/Pixelmax-Regular.otf')
        self.pixelade_font = os.path.join(base_path, 'assets/fonts/PIXELADE.TTF')
        
        # Background
        with self.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        # Title
        self.title = Label(
            text='SELECT DIFFICULTY',
            font_size=48,
            font_name=self.pixelmax_font,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.85},
            size_hint=(None, None)
        )
        self.add_widget(self.title)
        
        # Difficulty buttons with descriptions
        self._create_difficulty_buttons()
        
        # Back button
        self.back_btn = Button(
            text='Back',
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.08},
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=24,
            font_name=self.pixelade_font
        )
        self.back_btn.bind(on_press=self.on_back)
        self.add_widget(self.back_btn)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _create_difficulty_buttons(self):
        """Create difficulty selection buttons."""
        difficulties = [
            ('easy', 'EASY', 'Relaxed gameplay\nBot reacts slowly', (0.3, 0.7, 0.3, 1), 0.68),
            ('medium', 'MEDIUM', 'Balanced challenge\nBot is moderately skilled', (0.7, 0.7, 0.3, 1), 0.53),
            ('hard', 'HARD', 'Tough opponent\nBot reacts quickly', (0.8, 0.4, 0.2, 1), 0.38),
            ('nightmare', 'NIGHTMARE', 'Brutal difficulty\nBot shows no mercy', (0.8, 0.1, 0.1, 1), 0.23),
        ]
        
        for diff_id, name, desc, color, y_pos in difficulties:
            # Button
            btn = Button(
                text=name,
                size_hint=(None, None),
                size=(200, 60),
                pos_hint={'center_x': 0.35, 'center_y': y_pos},
                background_color=color,
                font_size=28,
                font_name=self.pixelade_font,
                bold=True
            )
            btn.difficulty = diff_id
            btn.bind(on_press=self.on_difficulty_select)
            self.add_widget(btn)
            
            # Description label
            desc_label = Label(
                text=desc,
                font_size=18,
                font_name=self.pixelade_font,
                color=(0.8, 0.8, 0.8, 1),
                pos_hint={'center_x': 0.65, 'center_y': y_pos},
                size_hint=(None, None),
                halign='left',
                valign='middle'
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            self.add_widget(desc_label)
    
    def on_difficulty_select(self, instance):
        """Handle difficulty selection."""
        difficulty = instance.difficulty
        
        # Set difficulty on the game screen's bot
        if hasattr(self.app, 'screens') and SCREENS['GAME'] in self.app.screens:
            game_screen = self.app.screens[SCREENS['GAME']]
            game_screen.set_difficulty(difficulty)
            game_screen.reset_game()
        
        # Store selected difficulty in app for future reference
        self.app.selected_difficulty = difficulty
        
        # Go to game
        self.app.switch_screen(SCREENS['GAME'])
    
    def on_back(self, instance):
        """Go back to previous screen."""
        self.app.switch_screen(SCREENS['START'])
    
    def on_enter(self):
        """Called when entering this screen."""
        pass
    
    def on_leave(self):
        """Called when leaving this screen."""
        pass
