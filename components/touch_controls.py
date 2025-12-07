"""
Touch Controls Component
Handles on-screen touch buttons for mobile gameplay
"""

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window

from config import BUTTON_SIZE, COLORS


class TouchControls(Widget):
    """Container for all touch control buttons."""
    
    def __init__(self, game_widget, **kwargs):
        super().__init__(**kwargs)
        self.game = game_widget
        self.p1_controls = []
        self.p2_controls = []
        self.labels = []
    
    def create_controls(self, layout):
        """Create all touch control buttons and add to layout."""
        self._create_p1_controls(layout)
        self._create_p2_controls(layout)
        self._create_labels(layout)
    
    def _create_p1_controls(self, layout):
        """Create Player 1 controls (left side)."""
        btn_size = BUTTON_SIZE
        
        # Left button
        p1_left = Button(
            text='<',
            size_hint=(None, None),
            size=btn_size,
            pos=(20, 100),
            background_color=COLORS['p1_movement'],
            font_size=32
        )
        p1_left.bind(
            on_press=lambda btn: self._on_move_press(self.game.fighter_1, 'left', True),
            on_release=lambda btn: self._on_move_press(self.game.fighter_1, 'left', False)
        )
        layout.add_widget(p1_left)
        self.p1_controls.append(p1_left)
        
        # Right button
        p1_right = Button(
            text='>',
            size_hint=(None, None),
            size=btn_size,
            pos=(120, 100),
            background_color=COLORS['p1_movement'],
            font_size=32
        )
        p1_right.bind(
            on_press=lambda btn: self._on_move_press(self.game.fighter_1, 'right', True),
            on_release=lambda btn: self._on_move_press(self.game.fighter_1, 'right', False)
        )
        layout.add_widget(p1_right)
        self.p1_controls.append(p1_right)
        
        # Jump button
        p1_jump = Button(
            text='^',
            size_hint=(None, None),
            size=btn_size,
            pos=(70, 190),
            background_color=COLORS['jump'],
            font_size=32
        )
        p1_jump.bind(on_press=lambda btn: self.game.fighter_1.do_jump())
        layout.add_widget(p1_jump)
        self.p1_controls.append(p1_jump)
        
        # Attack 1
        p1_atk1 = Button(
            text='A1',
            size_hint=(None, None),
            size=btn_size,
            pos=(20, 10),
            background_color=COLORS['p1_attack'],
            font_size=24
        )
        p1_atk1.bind(on_press=lambda btn: self.game.fighter_1.do_attack(1))
        layout.add_widget(p1_atk1)
        self.p1_controls.append(p1_atk1)
        
        # Attack 2
        p1_atk2 = Button(
            text='A2',
            size_hint=(None, None),
            size=btn_size,
            pos=(120, 10),
            background_color=COLORS['p1_attack'],
            font_size=24
        )
        p1_atk2.bind(on_press=lambda btn: self.game.fighter_1.do_attack(2))
        layout.add_widget(p1_atk2)
        self.p1_controls.append(p1_atk2)
    
    def _create_p2_controls(self, layout):
        """Create Player 2 controls (right side)."""
        btn_size = BUTTON_SIZE
        base_x = Window.width - 200
        
        # Left button
        p2_left = Button(
            text='<',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x, 100),
            background_color=COLORS['p2_movement'],
            font_size=32
        )
        p2_left.bind(
            on_press=lambda btn: self._on_move_press(self.game.fighter_2, 'left', True),
            on_release=lambda btn: self._on_move_press(self.game.fighter_2, 'left', False)
        )
        layout.add_widget(p2_left)
        self.p2_controls.append(('left', p2_left, 0))
        
        # Right button
        p2_right = Button(
            text='>',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x + 100, 100),
            background_color=COLORS['p2_movement'],
            font_size=32
        )
        p2_right.bind(
            on_press=lambda btn: self._on_move_press(self.game.fighter_2, 'right', True),
            on_release=lambda btn: self._on_move_press(self.game.fighter_2, 'right', False)
        )
        layout.add_widget(p2_right)
        self.p2_controls.append(('right', p2_right, 100))
        
        # Jump button
        p2_jump = Button(
            text='^',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x + 50, 190),
            background_color=COLORS['jump'],
            font_size=32
        )
        p2_jump.bind(on_press=lambda btn: self.game.fighter_2.do_jump())
        layout.add_widget(p2_jump)
        self.p2_controls.append(('jump', p2_jump, 50))
        
        # Attack 1
        p2_atk1 = Button(
            text='A1',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x, 10),
            background_color=COLORS['p2_attack'],
            font_size=24
        )
        p2_atk1.bind(on_press=lambda btn: self.game.fighter_2.do_attack(1))
        layout.add_widget(p2_atk1)
        self.p2_controls.append(('atk1', p2_atk1, 0))
        
        # Attack 2
        p2_atk2 = Button(
            text='A2',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x + 100, 10),
            background_color=COLORS['p2_attack'],
            font_size=24
        )
        p2_atk2.bind(on_press=lambda btn: self.game.fighter_2.do_attack(2))
        layout.add_widget(p2_atk2)
        self.p2_controls.append(('atk2', p2_atk2, 100))
    
    def _create_labels(self, layout):
        """Create player labels."""
        base_x = Window.width - 200
        
        p1_label = Label(
            text='P1',
            pos=(70, 280),
            size_hint=(None, None),
            font_size=20,
            color=(0.3, 0.3, 1, 1)
        )
        layout.add_widget(p1_label)
        self.labels.append(p1_label)
        
        p2_label = Label(
            text='P2',
            pos=(base_x + 50, 280),
            size_hint=(None, None),
            font_size=20,
            color=(1, 0.6, 0.3, 1)
        )
        layout.add_widget(p2_label)
        self.labels.append(p2_label)
        self.p2_label = p2_label
    
    def reposition_p2_controls(self, screen_width):
        """Reposition P2 controls based on screen width."""
        base_x = screen_width - 200
        
        for item in self.p2_controls:
            name, btn, offset = item
            if name == 'jump':
                btn.pos = (base_x + offset, 190)
            elif name in ('atk1', 'atk2'):
                btn.pos = (base_x + offset, 10)
            else:
                btn.pos = (base_x + offset, 100)
        
        if hasattr(self, 'p2_label'):
            self.p2_label.pos = (base_x + 50, 280)
    
    def _on_move_press(self, fighter, direction, pressed):
        """Handle movement button press/release."""
        if direction == 'left':
            fighter.move_left = pressed
        elif direction == 'right':
            fighter.move_right = pressed
    
    def show(self):
        """Show all controls."""
        for btn in self.p1_controls:
            btn.opacity = 1
            btn.disabled = False
        for item in self.p2_controls:
            item[1].opacity = 1
            item[1].disabled = False
        for label in self.labels:
            label.opacity = 1
    
    def hide(self):
        """Hide all controls."""
        for btn in self.p1_controls:
            btn.opacity = 0
            btn.disabled = True
        for item in self.p2_controls:
            item[1].opacity = 0
            item[1].disabled = True
        for label in self.labels:
            label.opacity = 0
