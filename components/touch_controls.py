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


class TouchControls(Widget):
    """Container for Player 1 touch control buttons with responsive scaling."""
    
    def __init__(self, game_widget, **kwargs):
        super().__init__(**kwargs)
        self.game = game_widget
        self.controls = []
        self.layout = None
        
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
    
    def get_button_size(self):
        """Get scaled button size."""
        scale = self.get_scale_factor()
        base_size = 80
        size = int(base_size * scale)
        return (size, size)
    
    def get_font_size(self, base_size=32):
        """Get scaled font size."""
        scale = self.get_scale_factor()
        return int(base_size * scale)
    
    def create_controls(self, layout):
        """Create all touch control buttons and add to layout."""
        self.layout = layout
        self._create_movement_controls(layout)
        self._create_action_controls(layout)
    
    def _create_movement_controls(self, layout):
        """Create movement controls (left side of screen)."""
        btn_size = self.get_button_size()
        scale = self.get_scale_factor()
        margin = int(20 * scale)
        spacing = int(10 * scale)
        
        # Left button - bottom left
        left_btn = Button(
            text='<',
            size_hint=(None, None),
            size=btn_size,
            pos=(margin, margin + btn_size[1] + spacing),
            background_color=COLORS['p1_movement'],
            font_size=self.get_font_size(32)
        )
        left_btn.name = 'left'
        left_btn.bind(
            on_press=lambda btn: self._on_move_press('left', True),
            on_release=lambda btn: self._on_move_press('left', False)
        )
        layout.add_widget(left_btn)
        self.controls.append(left_btn)
        
        # Right button - next to left
        right_btn = Button(
            text='>',
            size_hint=(None, None),
            size=btn_size,
            pos=(margin + btn_size[0] + spacing, margin + btn_size[1] + spacing),
            background_color=COLORS['p1_movement'],
            font_size=self.get_font_size(32)
        )
        right_btn.name = 'right'
        right_btn.bind(
            on_press=lambda btn: self._on_move_press('right', True),
            on_release=lambda btn: self._on_move_press('right', False)
        )
        layout.add_widget(right_btn)
        self.controls.append(right_btn)
    
    def _create_action_controls(self, layout):
        """Create action controls (right side of screen) - Jump and Attack."""
        btn_size = self.get_button_size()
        scale = self.get_scale_factor()
        margin = int(20 * scale)
        spacing = int(10 * scale)
        
        # Calculate right side positions
        right_base = Window.width - margin - btn_size[0] * 2 - spacing
        
        # Attack 1 - bottom right area
        atk1_btn = Button(
            text='A1',
            size_hint=(None, None),
            size=btn_size,
            pos=(right_base, margin),
            background_color=COLORS['p1_attack'],
            font_size=self.get_font_size(24)
        )
        atk1_btn.name = 'atk1'
        atk1_btn.bind(
            on_press=lambda btn: self._on_attack_press(1),
            on_release=lambda btn: self._on_attack_release(1)
        )
        layout.add_widget(atk1_btn)
        self.controls.append(atk1_btn)
        
        # Attack 2 - next to A1
        atk2_btn = Button(
            text='A2',
            size_hint=(None, None),
            size=btn_size,
            pos=(right_base + btn_size[0] + spacing, margin),
            background_color=COLORS['p1_attack'],
            font_size=self.get_font_size(24)
        )
        atk2_btn.name = 'atk2'
        atk2_btn.bind(
            on_press=lambda btn: self._on_attack_press(2),
            on_release=lambda btn: self._on_attack_release(2)
        )
        layout.add_widget(atk2_btn)
        self.controls.append(atk2_btn)
        
        # Jump button - above attack buttons, centered
        jump_btn = Button(
            text='^',
            size_hint=(None, None),
            size=btn_size,
            pos=(right_base + (btn_size[0] + spacing) // 2, margin + btn_size[1] + spacing),
            background_color=COLORS['jump'],
            font_size=self.get_font_size(32)
        )
        jump_btn.name = 'jump'
        jump_btn.bind(on_press=lambda btn: self._on_jump())
        layout.add_widget(jump_btn)
        self.controls.append(jump_btn)
    
    def on_window_resize(self, window, size):
        """Reposition and resize all controls on window resize."""
        self.reposition_controls()
    
    def reposition_controls(self):
        """Reposition all controls based on current screen size."""
        btn_size = self.get_button_size()
        scale = self.get_scale_factor()
        margin = int(20 * scale)
        spacing = int(10 * scale)
        
        right_base = Window.width - margin - btn_size[0] * 2 - spacing
        
        for btn in self.controls:
            btn.size = btn_size
            
            if btn.name == 'left':
                btn.pos = (margin, margin + btn_size[1] + spacing)
                btn.font_size = self.get_font_size(32)
            elif btn.name == 'right':
                btn.pos = (margin + btn_size[0] + spacing, margin + btn_size[1] + spacing)
                btn.font_size = self.get_font_size(32)
            elif btn.name == 'atk1':
                btn.pos = (right_base, margin)
                btn.font_size = self.get_font_size(24)
            elif btn.name == 'atk2':
                btn.pos = (right_base + btn_size[0] + spacing, margin)
                btn.font_size = self.get_font_size(24)
            elif btn.name == 'jump':
                btn.pos = (right_base + (btn_size[0] + spacing) // 2, margin + btn_size[1] + spacing)
                btn.font_size = self.get_font_size(32)
    
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
        
        # Track which buttons are pressed
        self.attack_buttons_pressed.add(attack_type)
        
        # Check for combo (both buttons pressed)
        if 1 in self.attack_buttons_pressed and 2 in self.attack_buttons_pressed:
            self.game.fighter_1.do_attack(3)  # Combo attack!
        else:
            self.game.fighter_1.do_attack(attack_type)
    
    def _on_attack_release(self, attack_type):
        """Handle attack button release."""
        self.attack_buttons_pressed.discard(attack_type)
    
    def _on_jump(self):
        """Handle jump button press."""
        # Ignore input if game is over
        if hasattr(self.game, 'game_over') and self.game.game_over:
            return
        self.game.fighter_1.do_jump()
    
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
