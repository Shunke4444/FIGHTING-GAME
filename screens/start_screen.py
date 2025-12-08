"""
Start Screen
The initial screen shown when the game launches
Tap anywhere to start the game
"""

import os
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
from kivy.animation import Animation
from kivy.clock import Clock

from screens.base_screen import BaseScreen
from config import SCREENS


class StartScreen(BaseScreen):
    """Start screen with parallax background and tap to start."""

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

        # Bind resize events
        self.bind(size=self._on_size_change, pos=self._on_size_change)

        # Load background layers
        self._load_background()

        # Load pixel fonts
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pixelmax_font = os.path.join(base_path, 'assets/fonts/Pixelmax-Regular.otf')
        self.pixelade_font = os.path.join(base_path, 'assets/fonts/PIXELADE.TTF')

        # TITLE LABEL
        self.title_label = Label(
            text='FOREST FIGHTER II',
            font_size=64,
            font_name=self.pixelmax_font,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.65},
            size_hint=(None, None),
            outline_width=2,
            outline_color=(0.05, 0.5, 0.15, 1)
        )
        self.add_widget(self.title_label)

        # START LABEL
        self.start_label = Label(
            text='Tap anywhere to start',
            font_size=32,
            font_name=self.pixelade_font,
            color=(1, 1, 1, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.40},
            size_hint=(None, None)
        )
        self.add_widget(self.start_label)

        # OPTIONS BUTTON (Image)
        options_img_path = os.path.join(base_path, 'assets/images/ui/Options.png')
        self.options_btn = Button(
            size_hint=(0.45, 0.25),
            pos_hint={'center_x': 0.5, 'center_y': 0.20},
            background_normal=options_img_path,
            background_down=options_img_path
        )
        self.options_btn.bind(on_press=self._on_options)
        self.add_widget(self.options_btn)

        # Tap animation
        self._start_animation()

        # Tap anywhere
        self.bind(on_touch_down=self.on_tap)

    # -------------------------------------------------------
    # PARALLAX BACKGROUND
    # -------------------------------------------------------

    def _load_background(self):
        """Load 4 parallax layers."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.bg_layers = []
        self.bg_x = [0, 0, 0, 0]  # X positions

        for i in range(1, 5):
            bg_path = os.path.join(base_path, f'assets/images/backgrounds/forestBackground/{i}.png')
            try:
                tex = CoreImage(bg_path).texture
                tex.wrap = 'repeat'
                self.bg_layers.append(tex)
            except:
                print(f"Error loading background layer: {bg_path}")

        # Parallax speeds (rear → front)
        self.parallax_speed = [0.1, 0.25, 0.45, 0.75]

        self._build_parallax_canvas()

    def _build_parallax_canvas(self):
        """Create rectangles for each layer with tiling support."""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rects = []
            
            # Draw in reverse order so layer 4 (foreground) is on top
            for i in range(len(self.bg_layers) - 1, -1, -1):
                tex = self.bg_layers[i]
                # Draw two copies of each texture for seamless scrolling
                for offset in [0, tex.width]:
                    rect = Rectangle(
                        texture=tex,
                        pos=(self.bg_x[i] + offset, 0),
                        size=self.size
                    )
                    self.bg_rects.append((i, offset, rect))

    def _update_parallax(self, dt):
        """Scroll parallax layers each frame."""
        for i in range(len(self.bg_layers)):
            self.bg_x[i] -= self.parallax_speed[i]

            # Loop when past edge
            if self.bg_x[i] <= -self.bg_layers[i].width:
                self.bg_x[i] = 0

        # Rebuild canvas with new positions
        self._build_parallax_canvas()

    # -------------------------------------------------------
    # UI + EVENTS
    # -------------------------------------------------------

    def _start_animation(self):
        """Pulse effect for 'Tap to Start'."""
        anim = Animation(opacity=0.3, duration=0.8) + Animation(opacity=1, duration=0.8)
        anim.repeat = True
        anim.start(self.start_label)

    def _on_options(self, instance):
        self.app.switch_screen(SCREENS['SETTINGS'])

    def on_tap(self, instance, touch):
        if self.options_btn.collide_point(*touch.pos):
            return False

        if self.collide_point(*touch.pos):
            self.app.switch_screen(SCREENS['DIFFICULTY_SELECT'])
            return True

        return False

    # -------------------------------------------------------
    # RESIZE + SCREEN TRANSITIONS
    # -------------------------------------------------------

    def _on_size_change(self, *args):
        """Resize parallax background."""
        if hasattr(self, "bg_rects"):
            self._build_parallax_canvas()

    def on_enter(self):
        """Start animations on screen entry."""
        self._build_parallax_canvas()

        # Pulse title
        anim = Animation(font_size=70, duration=0.6) + Animation(font_size=64, duration=0.6)
        anim.repeat = True
        anim.start(self.title_label)

    def on_leave(self):
        """Stop animations when leaving screen."""
        Animation.cancel_all(self.start_label)
        Animation.cancel_all(self.title_label)
