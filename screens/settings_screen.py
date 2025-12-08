"""
Settings Screen
Options menu for game settings
"""

import os
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window

from screens.base_screen import BaseScreen
from utils.settings import SettingsManager
from config import SCREENS


class SettingsScreen(BaseScreen):
    """Settings menu screen."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.settings = SettingsManager.get_instance()
        self._create_ui()
    
    def _create_ui(self):
        """Create the settings UI."""
        # Load pixel fonts
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pixelmax_font = os.path.join(base_path, 'assets/fonts/Pixelmax-Regular.otf')
        self.pixelade_font = os.path.join(base_path, 'assets/fonts/PIXELADE.TTF')
        
        # Background
        with self.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg)
        
        # Main vertical layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Title
        self.title = Label(
            text='SETTINGS',
            font_size=56,
            font_name=self.pixelmax_font,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=70
        )
        main_layout.add_widget(self.title)
        
        # Scrollable content
        scroll_view = ScrollView(size_hint=(1, 1))
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint=(1, None),
            padding=10
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Control Layout button
        controls_btn = Button(
            text='Control Layout',
            font_size=28,
            font_name=self.pixelade_font,
            background_color=(0.3, 0.5, 0.8, 1),
            size_hint=(1, None),
            height=60
        )
        controls_btn.bind(on_press=self._on_controls)
        content_layout.add_widget(controls_btn)
        
        # Reset Controls button
        reset_btn = Button(
            text='Reset Controls to Default',
            font_size=28,
            font_name=self.pixelade_font,
            background_color=(0.7, 0.3, 0.3, 1),
            size_hint=(1, None),
            height=60
        )
        reset_btn.bind(on_press=self._on_reset_controls)
        content_layout.add_widget(reset_btn)
        
        # Audio Settings Section
        audio_label = Label(
            text='AUDIO',
            font_size=32,
            font_name=self.pixelmax_font,
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint=(1, None),
            height=50
        )
        content_layout.add_widget(audio_label)
        
        # Music Volume Slider
        music_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)
        music_label = Label(text='Music:', font_size=26, font_name=self.pixelade_font, size_hint=(0.3, 1), halign='left')
        music_label.bind(size=music_label.setter('text_size'))
        self.music_slider = Slider(min=0, max=100, value=self.settings.get_music_volume() * 100, size_hint=(0.55, 1))
        self.music_slider.bind(value=self._on_music_volume_change)
        self.music_value_label = Label(text=f'{int(self.music_slider.value)}%', font_size=24, font_name=self.pixelade_font, size_hint=(0.15, 1))
        music_row.add_widget(music_label)
        music_row.add_widget(self.music_slider)
        music_row.add_widget(self.music_value_label)
        content_layout.add_widget(music_row)
        
        # SFX Volume Slider
        sfx_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)
        sfx_label = Label(text='SFX:', font_size=26, font_name=self.pixelade_font, size_hint=(0.3, 1), halign='left')
        sfx_label.bind(size=sfx_label.setter('text_size'))
        self.sfx_slider = Slider(min=0, max=100, value=self.settings.get_sfx_volume() * 100, size_hint=(0.55, 1))
        self.sfx_slider.bind(value=self._on_sfx_volume_change)
        self.sfx_value_label = Label(text=f'{int(self.sfx_slider.value)}%', font_size=24, font_name=self.pixelade_font, size_hint=(0.15, 1))
        sfx_row.add_widget(sfx_label)
        sfx_row.add_widget(self.sfx_slider)
        sfx_row.add_widget(self.sfx_value_label)
        content_layout.add_widget(sfx_row)
        
        # Attack Sequences Section
        attack_label = Label(
            text='ATTACK SEQUENCES',
            font_size=32,
            font_name=self.pixelmax_font,
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint=(1, None),
            height=50
        )
        content_layout.add_widget(attack_label)
        
        # Define attack sequences
        attacks = [
            ('Attack A (A)', 'J key / A button', 'Quick jab attack'),
            ('Attack B (B)', 'K key / B button', 'Strong punch attack'),
            ('Attack C (Combo)', 'B + Direction', 'Powerful combo attack\n(Press B while moving left/right)'),
            ('Jump', 'W key / ^ button', 'Jump into the air'),
            ('Dash/Dodge', 'SPACE key / DASH button', 'Quick dash to evade attacks'),
            ('Move Left', 'A key / < button', 'Move left'),
            ('Move Right', 'D key / > button', 'Move right'),
        ]
        
        for attack_name, keys, description in attacks:
            attack_row = self._create_attack_row(attack_name, keys, description)
            content_layout.add_widget(attack_row)
        
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        
        # Back button
        back_btn = Button(
            text='Back',
            font_size=28,
            font_name=self.pixelade_font,
            background_color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, None),
            height=60
        )
        back_btn.bind(on_press=self._on_back)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
    
    def _create_attack_row(self, attack_name, keys, description):
        """Create a single attack sequence row."""
        attack_row = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, None), height=80, padding=5)
        
        # Left side: Attack name and description
        left_layout = BoxLayout(orientation='vertical', spacing=3, size_hint=(0.65, 1))
        
        name_label = Label(
            text=attack_name,
            font_size=20,
            font_name=self.pixelmax_font,
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint=(1, 0.4),
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        left_layout.add_widget(name_label)
        
        desc_label = Label(
            text=description,
            font_size=20,
            font_name=self.pixelade_font,
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, 0.6),
            halign='left',
            valign='top'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        left_layout.add_widget(desc_label)
        
        attack_row.add_widget(left_layout)
        
        # Right side: Keys/buttons
        keys_label = Label(
            text=keys,
            font_size=20,
            font_name=self.pixelade_font,
            color=(0.8, 0.8, 1, 1),
            size_hint=(0.35, 1),
            halign='right',
            valign='middle'
        )
        keys_label.bind(size=keys_label.setter('text_size'))
        attack_row.add_widget(keys_label)
        
        return attack_row
    
    def _update_bg(self, *args):
        """Update background size."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _on_controls(self, instance):
        """Open control layout editor."""
        self.app.switch_screen(SCREENS['CONTROL_LAYOUT'])
    
    def _on_reset_controls(self, instance):
        """Reset controls to default layout."""
        self.settings.reset_to_default()
        # Show feedback by briefly changing button color
        instance.background_color = (0.3, 0.7, 0.3, 1)
        instance.text = 'Controls Reset!'
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._restore_reset_button(instance), 1.0)
    
    def _restore_reset_button(self, btn):
        """Restore reset button to original state."""
        btn.background_color = (0.7, 0.3, 0.3, 1)
        btn.text = 'Reset Controls to Default'
    
    def _on_music_volume_change(self, instance, value):
        """Handle music volume slider change."""
        volume = value / 100.0
        self.settings.set_music_volume(volume)
        self.music_value_label.text = f'{int(value)}%'
        # Apply to game screen if it exists
        if hasattr(self.app, 'screens') and SCREENS['GAME'] in self.app.screens:
            game_screen = self.app.screens[SCREENS['GAME']]
            if game_screen.bg_music:
                game_screen.bg_music.volume = volume
                game_screen.music_original_volume = volume
    
    def _on_sfx_volume_change(self, instance, value):
        """Handle SFX volume slider change."""
        volume = value / 100.0
        self.settings.set_sfx_volume(volume)
        self.sfx_value_label.text = f'{int(value)}%'
        # Apply to fighters if game screen exists
        if hasattr(self.app, 'screens') and SCREENS['GAME'] in self.app.screens:
            game_screen = self.app.screens[SCREENS['GAME']]
            game_screen.apply_sfx_volume(volume)
    
    def _on_back(self, instance):
        """Go back to start screen."""
        self.app.switch_screen(SCREENS['START'])
    
    def on_enter(self):
        """Called when entering this screen."""
        # Update audio sliders to current values
        self.music_slider.value = self.settings.get_music_volume() * 100
        self.sfx_slider.value = self.settings.get_sfx_volume() * 100
        self.music_value_label.text = f'{int(self.music_slider.value)}%'
        self.sfx_value_label.text = f'{int(self.sfx_slider.value)}%'
    
    def on_leave(self):
        """Called when leaving this screen."""
        pass
