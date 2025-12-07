"""
Game Screen
The main fighting gameplay screen
"""

import os
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

from screens.base_screen import BaseScreen
from components.fighter import Fighter
from components.touch_controls import TouchControls
from components.health_bar import HealthBar
from config import SCREENS, GROUND_Y, FPS, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, HEALTH_BAR_OFFSET_Y


class GameWidget(Widget):
    """The game rendering widget."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.screen_width = Window.width
        self.screen_height = Window.height
        self.size = (self.screen_width, self.screen_height)
        self.pos = (0, 0)
        
        # Create fighters
        fighter_start_y = GROUND_Y
        self.fighter_1 = Fighter(200, fighter_start_y, 'fantasy_warrior', is_player_2=False)
        self.fighter_2 = Fighter(self.screen_width - 300, fighter_start_y, 'knight', is_player_2=True)
        
        # Create health bars
        self.health_bar_1 = HealthBar(20, self.screen_height - HEALTH_BAR_OFFSET_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        self.health_bar_2 = HealthBar(self.screen_width - HEALTH_BAR_WIDTH - 20, self.screen_height - HEALTH_BAR_OFFSET_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, is_flipped=True)
        
        # Load background
        self._load_background()
        
        # Keyboard input (for desktop testing)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self._on_key_down)
            self._keyboard.bind(on_key_up=self._on_key_up)
        self.keys_pressed = set()
        
        # Bind to window size
        Window.bind(size=self.on_window_resize)
    
    def _load_background(self):
        """Load background texture."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(base_path, 'assets/images/backgrounds/FOREST.png')
        
        try:
            self.bg_texture = CoreImage(bg_path).texture
        except:
            self.bg_texture = None
            print(f"Warning: Could not load background from {bg_path}")
    
    def on_window_resize(self, window, size):
        """Handle window resize."""
        self.screen_width = size[0]
        self.screen_height = size[1]
        self.size = size
        
        # Update health bar positions
        self.health_bar_1.update_position(20, self.screen_height - HEALTH_BAR_OFFSET_Y)
        self.health_bar_2.update_position(self.screen_width - HEALTH_BAR_WIDTH - 20, self.screen_height - HEALTH_BAR_OFFSET_Y)
    
    def _on_keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        self.keys_pressed.add(key)
        
        # Player 1 Jump
        if key == 'w':
            self.fighter_1.do_jump()
        # Player 2 Jump
        if key == 'up':
            self.fighter_2.do_jump()
        
        return True
    
    def _on_key_up(self, keyboard, keycode):
        key = keycode[1]
        self.keys_pressed.discard(key)
        return True
    
    def update(self, dt):
        """Main game loop."""
        self.screen_width = Window.width
        self.screen_height = Window.height
        
        # Handle keyboard movement for Player 1 (OR with touch controls)
        if 'a' in self.keys_pressed:
            self.fighter_1.move_left = True
        if 'd' in self.keys_pressed:
            self.fighter_1.move_right = True
        
        # Handle keyboard attacks for Player 1
        if 'j' in self.keys_pressed and 'k' in self.keys_pressed:
            self.fighter_1.do_attack(3)
        elif 'j' in self.keys_pressed:
            self.fighter_1.do_attack(1)
        elif 'k' in self.keys_pressed:
            self.fighter_1.do_attack(2)
        
        # Handle keyboard movement for Player 2 (OR with touch controls)
        if 'left' in self.keys_pressed:
            self.fighter_2.move_left = True
        if 'right' in self.keys_pressed:
            self.fighter_2.move_right = True
        
        # Handle keyboard attacks for Player 2
        if ',' in self.keys_pressed and '.' in self.keys_pressed:
            self.fighter_2.do_attack(3)
        elif ',' in self.keys_pressed:
            self.fighter_2.do_attack(1)
        elif '.' in self.keys_pressed:
            self.fighter_2.do_attack(2)
        
        # Update fighters
        self.fighter_1.move(self.screen_width, self.screen_height, self.fighter_2)
        self.fighter_2.move(self.screen_width, self.screen_height, self.fighter_1)
        
        # Update animations
        self.fighter_1.update_animation()
        self.fighter_2.update_animation()
        
        # Check attacks
        self.fighter_1.check_attack_hit(self.fighter_2)
        self.fighter_2.check_attack_hit(self.fighter_1)
        
        # Check for game over
        if not self.fighter_1.alive or not self.fighter_2.alive:
            # Could trigger game over screen here
            pass
        
        # Redraw
        self.draw_game()
    
    def draw_game(self):
        """Draw the game."""
        self.canvas.clear()
        
        with self.canvas:
            # Draw background
            if self.bg_texture:
                Rectangle(texture=self.bg_texture, pos=(0, 0), 
                         size=(self.screen_width, self.screen_height))
            else:
                Color(0.2, 0.4, 0.3, 1)
                Rectangle(pos=(0, 0), size=(self.screen_width, self.screen_height))
        
        # Draw health bars
        self.health_bar_1.draw(self.canvas, self.fighter_1.health)
        self.health_bar_2.draw(self.canvas, self.fighter_2.health)
        
        # Draw fighters
        self._draw_fighter(self.fighter_1)
        self._draw_fighter(self.fighter_2)
    
    def _draw_fighter(self, fighter):
        """Draw a fighter."""
        if fighter.current_texture is None:
            return
        
        draw_x, draw_y = fighter.get_draw_pos()
        
        with self.canvas:
            Color(1, 1, 1, 1)
            
            texture = fighter.current_texture
            
            # Handle flip
            if fighter.flip:
                texture = texture.get_region(0, 0, texture.width, texture.height)
                texture.flip_horizontal()
            
            Rectangle(
                texture=texture,
                pos=(draw_x, draw_y),
                size=(fighter.scale_width, fighter.scale_height)
            )
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.fighter_1.reset(200, GROUND_Y)
        self.fighter_2.reset(self.screen_width - 300, GROUND_Y)


class GameScreen(BaseScreen):
    """The main game screen."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Create game widget
        self.game_widget = GameWidget(size_hint=(1, 1))
        self.add_widget(self.game_widget)
        
        # Create touch controls
        self.touch_controls = TouchControls(self.game_widget)
        self.touch_controls.create_controls(self)
        
        # Create pause button
        self.pause_btn = Button(
            text='||',
            size_hint=(None, None),
            size=(60, 60),
            pos=(Window.width // 2 - 30, Window.height - 70),
            background_color=(0.5, 0.5, 0.5, 0.7),
            font_size=28
        )
        self.pause_btn.bind(on_press=self.on_pause)
        self.add_widget(self.pause_btn)
        
        # Game loop event
        self.game_event = None
    
    def on_enter(self):
        """Start the game loop when entering."""
        self.game_event = Clock.schedule_interval(self.update, 1.0 / FPS)
    
    def on_leave(self):
        """Stop the game loop when leaving."""
        if self.game_event:
            self.game_event.cancel()
            self.game_event = None
    
    def update(self, dt):
        """Update the game."""
        self.game_widget.update(dt)
    
    def on_pause(self, instance):
        """Handle pause button press."""
        self.app.switch_screen(SCREENS['PAUSE'])
    
    def on_window_resize(self, window, size):
        """Handle window resize."""
        self.touch_controls.reposition_p2_controls(size[0])
        self.pause_btn.pos = (size[0] // 2 - 30, size[1] - 70)
    
    def reset_game(self):
        """Reset the game."""
        self.game_widget.reset_game()
