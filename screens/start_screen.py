"""
Start Screen
The initial screen shown when the game launches
Tap anywhere to start the game
"""

import os
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
from kivy.animation import Animation

from screens.base_screen import BaseScreen
from config import SCREENS


class StartScreen(BaseScreen):
    """Start screen with 'Tap to Start' message."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Load background
        self._load_background()
        
        # Create title label
        self.title_label = Label(
            text='FIGHTING GAME',
            font_size=64,
            bold=True,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            size_hint=(None, None)
        )
        self.add_widget(self.title_label)
        
        # Create tap to start label
        self.start_label = Label(
            text='Tap anywhere to start',
            font_size=32,
            color=(1, 1, 1, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            size_hint=(None, None)
        )
        self.add_widget(self.start_label)
        
        # Animate the start label (pulsing effect)
        self._start_animation()
        
        # Bind touch event
        self.bind(on_touch_down=self.on_tap)
    
    def _load_background(self):
        """Load and set background image."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(base_path, 'assets/images/backgrounds/FOREST.png')
        
        try:
            self.bg_texture = CoreImage(bg_path).texture
        except:
            self.bg_texture = None
        
        self._draw_background()
    
    def _draw_background(self):
        """Draw the background."""
        self.canvas.before.clear()
        with self.canvas.before:
            if self.bg_texture:
                # Dim the background
                Color(0.5, 0.5, 0.5, 1)
                Rectangle(
                    texture=self.bg_texture,
                    pos=(0, 0),
                    size=self.size
                )
            else:
                Color(0.1, 0.2, 0.3, 1)
                Rectangle(pos=(0, 0), size=self.size)
    
    def _start_animation(self):
        """Start pulsing animation for the start label."""
        anim = Animation(opacity=0.3, duration=0.8) + Animation(opacity=1, duration=0.8)
        anim.repeat = True
        anim.start(self.start_label)
    
    def on_tap(self, instance, touch):
        """Handle tap to start the game."""
        if self.collide_point(*touch.pos):
            self.app.switch_screen(SCREENS['GAME'])
            return True
        return False
    
    def on_window_resize(self, window, size):
        """Handle window resize."""
        self._draw_background()
    
    def on_enter(self):
        """Called when entering this screen."""
        self._draw_background()
    
    def on_leave(self):
        """Called when leaving this screen."""
        Animation.cancel_all(self.start_label)
