"""
Touch Controls Component
Handles on-screen touch buttons for mobile gameplay
Scales automatically with screen size
"""

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window

from config import COLORS
from utils.settings import SettingsManager


class TouchControls(Widget):
    """Container for Player 1 touch control buttons with responsive scaling."""
    
    def __init__(self, game_widget, **kwargs):
        super().__init__(**kwargs)
        self.game = game_widget
        self.controls = []
        self.layout = None
        self.settings = SettingsManager.get_instance()
        
        # Track which attack buttons are pressed for combo
        self.attack_buttons_pressed = set()
        
        # Bind to window resize
        Window.bind(size=self.on_window_resize)
    
    def get_scale_factor(self):
        """Calculate scale factor based on screen size."""
        # Base size is 1000x600, scale proportionally
        base_width = 1000
        base_height = 600
        width_scale = Window.width / base_width
        height_scale = Window.height / base_height
        return min(width_scale, height_scale)
    
    def get_button_size(self, control_name=None):
        """Get scaled button size with user preference (individual or global)."""
        scale = self.get_scale_factor()
        if control_name:
            user_scale = self.settings.get_individual_button_scale(control_name)
        else:
            user_scale = self.settings.get_button_scale()
        base_size = 80
        size = int(base_size * scale * user_scale)
        return (size, size)
    
    def get_button_opacity(self, control_name=None):
        """Get user-configured button opacity (individual or global)."""
        if control_name:
            return self.settings.get_individual_button_opacity(control_name)
        return self.settings.get_button_opacity()
    
    def get_font_size(self, base_size=32, control_name=None):
        """Get scaled font size."""
        scale = self.get_scale_factor()
        if control_name:
            user_scale = self.settings.get_individual_button_scale(control_name)
        else:
            user_scale = self.settings.get_button_scale()
        return int(base_size * scale * user_scale)
    
    def create_controls(self, layout):
        """Create all touch control buttons and add to layout."""
        self.layout = layout
        self._create_movement_controls(layout)
        self._create_action_controls(layout)
    
    def _create_movement_controls(self, layout):
        """Create movement controls (left side of screen)."""
        controls = self.settings.get_controls()
        
        # Left button
        left_pos = controls.get('left', {'x': 0.02, 'y': 0.15})
        left_size = self.get_button_size('left')
        left_opacity = self.get_button_opacity('left')
        left_btn = Button(
            text='<',
            size_hint=(None, None),
            size=left_size,
            pos=(left_pos['x'] * Window.width, left_pos['y'] * Window.height),
            background_color=(*COLORS['p1_movement'][:3], left_opacity),
            font_size=self.get_font_size(32, 'left')
        )
        left_btn.name = 'left'
        left_btn.bind(
            on_press=lambda btn: self._on_move_press('left', True),
            on_release=lambda btn: self._on_move_press('left', False)
        )
        layout.add_widget(left_btn)
        self.controls.append(left_btn)
        
        # Right button
        right_pos = controls.get('right', {'x': 0.11, 'y': 0.15})
        right_size = self.get_button_size('right')
        right_opacity = self.get_button_opacity('right')
        right_btn = Button(
            text='>',
            size_hint=(None, None),
            size=right_size,
            pos=(right_pos['x'] * Window.width, right_pos['y'] * Window.height),
            background_color=(*COLORS['p1_movement'][:3], right_opacity),
            font_size=self.get_font_size(32, 'right')
        )
        right_btn.name = 'right'
        right_btn.bind(
            on_press=lambda btn: self._on_move_press('right', True),
            on_release=lambda btn: self._on_move_press('right', False)
        )
        layout.add_widget(right_btn)
        self.controls.append(right_btn)
    
    def _create_action_controls(self, layout):
        """Create action controls (right side of screen) - Jump, Attack, and Dash."""
        controls = self.settings.get_controls()
        
        # Attack 1
        atk1_pos = controls.get('atk1', {'x': 0.78, 'y': 0.03})
        atk1_size = self.get_button_size('atk1')
        atk1_opacity = self.get_button_opacity('atk1')
        atk1_btn = Button(
            text='A1',
            size_hint=(None, None),
            size=atk1_size,
            pos=(atk1_pos['x'] * Window.width, atk1_pos['y'] * Window.height),
            background_color=(*COLORS['p1_attack'][:3], atk1_opacity),
            font_size=self.get_font_size(24, 'atk1')
        )
        atk1_btn.name = 'atk1'
        atk1_btn.bind(
            on_press=lambda btn: self._on_attack_press(1),
            on_release=lambda btn: self._on_attack_release(1)
        )
        layout.add_widget(atk1_btn)
        self.controls.append(atk1_btn)
        
        # Attack 2
        atk2_pos = controls.get('atk2', {'x': 0.88, 'y': 0.03})
        atk2_size = self.get_button_size('atk2')
        atk2_opacity = self.get_button_opacity('atk2')
        atk2_btn = Button(
            text='A2',
            size_hint=(None, None),
            size=atk2_size,
            pos=(atk2_pos['x'] * Window.width, atk2_pos['y'] * Window.height),
            background_color=(*COLORS['p1_attack'][:3], atk2_opacity),
            font_size=self.get_font_size(24, 'atk2')
        )
        atk2_btn.name = 'atk2'
        atk2_btn.bind(
            on_press=lambda btn: self._on_attack_press(2),
            on_release=lambda btn: self._on_attack_release(2)
        )
        layout.add_widget(atk2_btn)
        self.controls.append(atk2_btn)
        
        # Jump button
        jump_pos = controls.get('jump', {'x': 0.88, 'y': 0.15})
        jump_size = self.get_button_size('jump')
        jump_opacity = self.get_button_opacity('jump')
        jump_btn = Button(
            text='^',
            size_hint=(None, None),
            size=jump_size,
            pos=(jump_pos['x'] * Window.width, jump_pos['y'] * Window.height),
            background_color=(*COLORS['jump'][:3], jump_opacity),
            font_size=self.get_font_size(32, 'jump')
        )
        jump_btn.name = 'jump'
        jump_btn.bind(on_press=lambda btn: self._on_jump())
        layout.add_widget(jump_btn)
        self.controls.append(jump_btn)
        
        # Dash button
        dodge_pos = controls.get('dodge', {'x': 0.78, 'y': 0.15})
        dodge_size = self.get_button_size('dodge')
        dodge_opacity = self.get_button_opacity('dodge')
        dash_btn = Button(
            text='DASH',
            size_hint=(None, None),
            size=dodge_size,
            pos=(dodge_pos['x'] * Window.width, dodge_pos['y'] * Window.height),
            background_color=(0.6, 0.3, 0.7, dodge_opacity),
            font_size=self.get_font_size(16, 'dodge')
        )
        dash_btn.name = 'dodge'
        dash_btn.bind(on_press=lambda btn: self._on_dodge())
        layout.add_widget(dash_btn)
        self.controls.append(dash_btn)
    
    def on_window_resize(self, window, size):
        """Reposition and resize all controls on window resize."""
        self.reposition_controls()
    
    def reposition_controls(self):
        """Reposition all controls based on current screen size and settings."""
        # Reload settings to get any changes made in the control layout screen
        self.settings.reload()
        
        controls = self.settings.get_controls()
        
        font_sizes = {
            'left': 32,
            'right': 32,
            'atk1': 24,
            'atk2': 24,
            'jump': 32,
            'dodge': 16,
        }
        
        for btn in self.controls:
            control_name = btn.name
            
            # Get individual button size and opacity
            btn_size = self.get_button_size(control_name)
            btn_opacity = self.get_button_opacity(control_name)
            
            btn.size = btn_size
            
            if control_name in controls and isinstance(controls[control_name], dict):
                pos_data = controls[control_name]
                btn.pos = (pos_data['x'] * Window.width, pos_data['y'] * Window.height)
            
            if control_name in font_sizes:
                btn.font_size = self.get_font_size(font_sizes[control_name], control_name)
            
            # Update opacity (keep original color RGB, just change alpha)
            color = btn.background_color
            btn.background_color = (color[0], color[1], color[2], btn_opacity)
    
    def _on_move_press(self, direction, pressed):
        """Handle movement button press/release."""
        # Ignore input if game is over
        if hasattr(self.game, 'game_over') and self.game.game_over:
            return
        
        if direction == 'left':
            self.game.fighter_1.move_left = pressed
        elif direction == 'right':
            self.game.fighter_1.move_right = pressed
    
    def _on_attack_press(self, attack_type):
        """Handle attack button press with combo detection."""
        # Ignore input if game is over
        if hasattr(self.game, 'game_over') and self.game.game_over:
            return
        
        # Check for combo: A2 while moving triggers Attack 3
        if attack_type == 2:
            fighter = self.game.fighter_1
            if fighter.move_left or fighter.move_right:
                self.game.fighter_1.do_attack(3)  # Directional combo attack!
                return
        
        self.game.fighter_1.do_attack(attack_type)
    
    def _on_attack_release(self, attack_type):
        """Handle attack button release."""
        pass  # No longer tracking for combo
    
    def _on_jump(self):
        """Handle jump button press."""
        # Ignore input if game is over
        if hasattr(self.game, 'game_over') and self.game.game_over:
            return
        self.game.fighter_1.do_jump()
    
    def _on_dodge(self):
        """Handle dodge button press."""
        # Ignore input if game is over
        if hasattr(self.game, 'game_over') and self.game.game_over:
            return
        self.game.fighter_1.do_dodge()
    
    def show(self):
        """Show all controls."""
        for btn in self.controls:
            btn.opacity = 1
            btn.disabled = False
    
    def hide(self):
        """Hide all controls."""
        for btn in self.controls:
            btn.opacity = 0
            btn.disabled = True
