import os
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

from screens.base_screen import BaseScreen
from config import SCREENS


def scale(value):
    """Scales UI values based on screen size."""
    base_width = 1920
    ratio = Window.width / base_width
    return value * ratio


class DifficultySelectScreen(BaseScreen):
    """Responsive difficulty selection screen."""

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pixelmax_font = os.path.join(base_path, 'assets/fonts/Pixelmax-Regular.otf')
        self.pixelade_font = os.path.join(base_path, 'assets/fonts/PIXELADE.TTF')

        # Load parallax background
        self._load_background()
        
        # Bind to size and position changes
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Layout
        layout = FloatLayout()

        # Title
        self.title = Label(
            text='SELECT DIFFICULTY',
            font_size=scale(120),
            font_name=self.pixelmax_font,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            size_hint=(1, None),
            height=scale(120)
        )
        layout.add_widget(self.title)

        self._create_difficulty_buttons(layout)

        # Back button
        self.back_btn = Button(
            text='BACK',
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            background_color=(0.4, 0.4, 0.4, 1),
            font_size=scale(50),
            font_name=self.pixelade_font
        )
        self.back_btn.bind(on_press=self.on_back)
        layout.add_widget(self.back_btn)

        self.add_widget(layout)

        # Listen to window resize
        Window.bind(on_resize=self._resize_ui)

    def _load_background(self):
        """Load CloudyForest parallax layers."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.bg_layers = []

        for i in range(1, 6):
            bg_path = os.path.join(base_path, f'assets/images/backgrounds/CloudyForest/bg-2_LAYER-{i}.png')
            try:
                tex = CoreImage(bg_path).texture
                self.bg_layers.append(tex)
            except Exception as e:
                print(f"Error loading background layer {i}: {e}")

        self._build_parallax_canvas()

    def _build_parallax_canvas(self):
        """Create rectangles for each layer stacked."""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            
            # Draw in reverse order so layer 5 (foreground) is on top
            if self.bg_layers:
                for i in range(len(self.bg_layers) - 1, -1, -1):
                    tex = self.bg_layers[i]
                    Rectangle(
                        texture=tex,
                        pos=(0, 0),
                        size=self.size
                    )
            else:
                # Fallback to solid color if no layers loaded
                Color(0.1, 0.1, 0.15, 1)
                Rectangle(pos=(0, 0), size=self.size)

    def _update_bg(self, *args):
        """Update background on resize."""
        self._build_parallax_canvas()

    def _resize_ui(self, *args):
        """Rescale UI dynamically on window resize."""
        self.title.font_size = scale(120)
        self.back_btn.font_size = scale(50)

        # Resize difficulty buttons & descriptions
        for child in self.children[0].children:
            if isinstance(child, Label) and child is not self.title:
                child.font_size = scale(36)

    def _create_difficulty_buttons(self, parent):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        difficulties = [
            ('easy', 'Easy.png', 'Relaxed gameplay\nBot reacts slowly', (0.18, 0.13), 0.78),
            ('medium', 'Medium.png', 'Balanced challenge\nBot is moderately skilled', (0.19, 0.16), 0.59),
            ('hard', 'Hard.png', 'Tough opponent\nBot reacts quickly', (0.18, 0.13), 0.40),
            ('nightmare', 'Nightmare.png', 'Brutal difficulty\nBot shows no mercy', (0.19, 0.17), 0.21),
        ]

        for diff_id, img_name, desc, size_hint, y in difficulties:
            img_path = os.path.join(base_path, f'assets/images/ui/difficult_select/{img_name}')
            
            # Button on the left
            btn = Button(
                size_hint=size_hint,
                pos_hint={'x': 0.25, 'center_y': y},
                background_normal=img_path,
                background_down=img_path
            )
            btn.difficulty = diff_id
            btn.bind(on_press=self.on_difficulty_select)
            parent.add_widget(btn)

            # Description to the right of button with gap
            desc_label = Label(
                text=desc,
                font_size=scale(36),
                font_name=self.pixelade_font,
                color=(0.8, 0.8, 0.8, 1),
                size_hint=(0.35, 0.11),
                pos_hint={'x': 0.50, 'center_y': y},
                halign='left',
                valign='middle'
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            parent.add_widget(desc_label)

    def on_difficulty_select(self, instance):
        difficulty = instance.difficulty
        if hasattr(self.app, 'screens') and SCREENS['GAME'] in self.app.screens:
            game = self.app.screens[SCREENS['GAME']]
            game.set_difficulty(difficulty)
            game.reset_game()

        self.app.selected_difficulty = difficulty
        self.app.switch_screen(SCREENS['GAME'])

    def on_back(self, instance):
        self.app.switch_screen(SCREENS['START'])
