"""
Settings Screen
Options menu for game settings
"""

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
        # Background
        with self.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg)
        
        # Title
        self.title = Label(
            text='SETTINGS',
            font_size=48,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        self.add_widget(self.title)
        
        # Main horizontal layout to hold buttons and combo list side by side
        main_layout = BoxLayout(
            orientation='horizontal',
            spacing=40,
            size_hint=(0.9, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.45}
        )
        
        # Left side: Buttons
        self.buttons_layout = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint=(0.4, 1)
        )
        
        # Control Layout button
        controls_btn = Button(
            text='Control Layout',
            font_size=28,
            background_color=(0.3, 0.5, 0.8, 1),
            size_hint=(1, None),
            height=70
        )
        controls_btn.bind(on_press=self._on_controls)
        self.buttons_layout.add_widget(controls_btn)
        
        # Reset Controls button
        reset_btn = Button(
            text='Reset Controls to Default',
            font_size=28,
            background_color=(0.7, 0.3, 0.3, 1),
            size_hint=(1, None),
            height=70
        )
        reset_btn.bind(on_press=self._on_reset_controls)
        self.buttons_layout.add_widget(reset_btn)
        
        # Audio Settings Section
        audio_label = Label(
            text='AUDIO',
            font_size=24,
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint=(1, None),
            height=40
        )
        self.buttons_layout.add_widget(audio_label)
        
        # Music Volume Slider
        music_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)
        music_label = Label(text='Music:', font_size=18, size_hint=(0.35, 1), halign='left')
        music_label.bind(size=music_label.setter('text_size'))
        self.music_slider = Slider(min=0, max=100, value=self.settings.get_music_volume() * 100, size_hint=(0.5, 1))
        self.music_slider.bind(value=self._on_music_volume_change)
        self.music_value_label = Label(text=f'{int(self.music_slider.value)}%', font_size=16, size_hint=(0.15, 1))
        music_row.add_widget(music_label)
        music_row.add_widget(self.music_slider)
        music_row.add_widget(self.music_value_label)
        self.buttons_layout.add_widget(music_row)
        
        # SFX Volume Slider
        sfx_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)
        sfx_label = Label(text='SFX:', font_size=18, size_hint=(0.35, 1), halign='left')
        sfx_label.bind(size=sfx_label.setter('text_size'))
        self.sfx_slider = Slider(min=0, max=100, value=self.settings.get_sfx_volume() * 100, size_hint=(0.5, 1))
        self.sfx_slider.bind(value=self._on_sfx_volume_change)
        self.sfx_value_label = Label(text=f'{int(self.sfx_slider.value)}%', font_size=16, size_hint=(0.15, 1))
        sfx_row.add_widget(sfx_label)
        sfx_row.add_widget(self.sfx_slider)
        sfx_row.add_widget(self.sfx_value_label)
        self.buttons_layout.add_widget(sfx_row)
        
        # Back button
        back_btn = Button(
            text='Back',
            font_size=28,
            background_color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, None),
            height=70
        )
        back_btn.bind(on_press=self._on_back)
        self.buttons_layout.add_widget(back_btn)
        
        # Spacer to push buttons to top
        self.buttons_layout.add_widget(Label(size_hint=(1, 1)))
        
        main_layout.add_widget(self.buttons_layout)
        
        # Right side: Attack Sequences / Combo List
        combo_panel = self._create_combo_panel()
        main_layout.add_widget(combo_panel)
        
        self.add_widget(main_layout)
    
    def _create_combo_panel(self):
        """Create the attack sequences / combo list panel."""
        # Container with background
        panel = FloatLayout(size_hint=(0.55, 1))
        
        with panel.canvas.before:
            Color(0.15, 0.15, 0.2, 0.9)
            self.panel_bg = Rectangle(pos=panel.pos, size=panel.size)
        panel.bind(pos=self._update_panel_bg, size=self._update_panel_bg)
        
        # Panel title
        panel_title = Label(
            text='ATTACK SEQUENCES',
            font_size=28,
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint=(1, None),
            height=40,
            pos_hint={'center_x': 0.5, 'top': 1}
        )
        panel.add_widget(panel_title)
        
        # Combo list content
        combo_content = BoxLayout(
            orientation='vertical',
            spacing=8,
            padding=[15, 10, 15, 10],
            size_hint=(1, 0.85),
            pos_hint={'center_x': 0.5, 'top': 0.88}
        )
        
        # Define attack sequences
        attacks = [
            ('Attack 1 (A1)', 'J key / A1 button', 'Quick jab attack'),
            ('Attack 2 (A2)', 'K key / A2 button', 'Strong punch attack'),
            ('Attack 3 (Combo)', 'A2 + Direction', 'Powerful combo attack\n(Press A2 while moving left/right)'),
            ('Jump', 'W key / ^ button', 'Jump into the air'),
            ('Dash/Dodge', 'SPACE key / DASH button', 'Quick dash to evade attacks'),
            ('Move Left', 'A key / < button', 'Move left'),
            ('Move Right', 'D key / > button', 'Move right'),
        ]
        
        for attack_name, keys, description in attacks:
            attack_row = self._create_attack_row(attack_name, keys, description)
            combo_content.add_widget(attack_row)
        
        panel.add_widget(combo_content)
        
        return panel
    
    def _create_attack_row(self, name, keys, description):
        """Create a single attack row for the combo list."""
        row = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, None),
            height=50
        )
        
        # Attack name (left side)
        name_label = Label(
            text=name,
            font_size=18,
            bold=True,
            color=(0.4, 0.8, 1, 1),
            size_hint=(0.3, 1),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        row.add_widget(name_label)
        
        # Keys/buttons (middle)
        keys_label = Label(
            text=keys,
            font_size=16,
            color=(1, 1, 0.5, 1),
            size_hint=(0.25, 1),
            halign='center',
            valign='middle'
        )
        keys_label.bind(size=keys_label.setter('text_size'))
        row.add_widget(keys_label)
        
        # Description (right side)
        desc_label = Label(
            text=description,
            font_size=14,
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(0.45, 1),
            halign='left',
            valign='middle'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        row.add_widget(desc_label)
        
        return row
    
    def _update_panel_bg(self, *args):
        """Update panel background."""
        if hasattr(self, 'panel_bg'):
            panel = args[0] if args else None
            if panel:
                self.panel_bg.pos = panel.pos
                self.panel_bg.size = panel.size
    
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
