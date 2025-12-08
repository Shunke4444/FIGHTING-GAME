"""
Start Screen
The initial screen shown when the game launches
Tap anywhere to start the game
"""

import os
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color, Line
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
        
        # Bind to size changes for responsive scaling
        self.bind(size=self._on_size_change, pos=self._on_size_change)
        
        # Load pixel fonts
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pixelmax_font = os.path.join(base_path, 'assets/fonts/Pixelmax-Regular.otf')
        self.pixelade_font = os.path.join(base_path, 'assets/fonts/PIXELADE.TTF')
        
        # Create title label with Pixelmax font (header)
        self.title_label = Label(
            text='FOREST FIGHTER II',
            font_size=64,
            font_name=self.pixelmax_font,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.65},
            size_hint=(None, None),
            outline_width=2,
            outline_color=(0.1, 1, 0.3, 1)
        )
        self.add_widget(self.title_label)
        
        # Create tap to start label with Pixelade font (body text)
        self.start_label = Label(
            text='Tap anywhere to start',
            font_size=32,
            font_name=self.pixelade_font,
            color=(1, 1, 1, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            size_hint=(None, None)
        )
        self.add_widget(self.start_label)
        
        # Create Options button with Pixelade font
        self.options_btn = Button(
            text='Options',
            font_size=24,
            font_name=self.pixelade_font,
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_color=(0.05, 0.35, 0.1, 0.9),
            background_normal='',
            background_down=''
        )
        self.options_btn.bind(on_press=self._on_options)
        self.add_widget(self.options_btn)
        
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
                # Display background without dimming
                Color(1, 1, 1, 1)
                Rectangle(
                    texture=self.bg_texture,
                    pos=self.pos,
                    size=self.size
                )
            else:
                Color(0.1, 0.2, 0.3, 1)
                Rectangle(pos=self.pos, size=self.size)
    
    def _start_animation(self):
        """Start pulsing animation for the start label."""
        anim = Animation(opacity=0.3, duration=0.8) + Animation(opacity=1, duration=0.8)
        anim.repeat = True
        anim.start(self.start_label)
    
    def _on_options(self, instance):
        """Open options/settings screen."""
        self.app.switch_screen(SCREENS['SETTINGS'])
    
    def on_tap(self, instance, touch):
        """Handle tap to start the game."""
        # Don't trigger if tapping the options button
        if self.options_btn.collide_point(*touch.pos):
            return False
        if self.collide_point(*touch.pos):
            self.app.switch_screen(SCREENS['DIFFICULTY_SELECT'])
            return True
        return False
    
    def on_window_resize(self, window, size):
        """Handle window resize."""
        self._draw_background()
    
    def _on_size_change(self, *args):
        """Handle size changes for responsive background."""
        self._draw_background()
    
    def on_enter(self):
        """Called when entering this screen."""
        self._draw_background()
        # Animate title with a scale pulse for extra pizzazz
        anim = Animation(font_size=70, duration=0.6) + Animation(font_size=64, duration=0.6)
        anim.repeat = True
        anim.start(self.title_label)
    
    def on_leave(self):
        """Called when leaving this screen."""
        Animation.cancel_all(self.start_label)
        Animation.cancel_all(self.title_label)
