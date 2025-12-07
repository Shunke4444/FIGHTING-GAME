"""
Game Screen
The main fighting gameplay screen
"""

import os
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.utils import platform

from screens.base_screen import BaseScreen
from components.fighter import Fighter
from components.touch_controls import TouchControls
from components.health_bar import HealthBar
from components.bot_ai import BotAI
from config import SCREENS, GROUND_Y, FPS


class GameWidget(Widget):
    """The game rendering widget."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.screen_width = Window.width
        self.screen_height = Window.height
        self.size = (self.screen_width, self.screen_height)
        self.pos = (0, 0)
        
        # Create fighters with scaled starting positions
        scale = self._get_scale_factor()
        fighter_start_y = int(GROUND_Y * scale)
        self.fighter_1 = Fighter(int(200 * scale), fighter_start_y, 'fantasy_warrior', is_player_2=False)
        self.fighter_2 = Fighter(int(self.screen_width - 300 * scale), fighter_start_y, 'knight', is_player_2=True)
        
        # Create bot AI for fighter 2
        self.bot_ai = BotAI(self.fighter_2, difficulty='medium')
        
        # Create health bars (now auto-scaling)
        self.health_bar_1 = HealthBar(is_flipped=False)
        self.health_bar_2 = HealthBar(is_flipped=True)
        
        # Game over state
        self.game_over = False
        self.game_over_timer = 0
        self.slow_motion_factor = 1.0
        self.winner = None  # 'player' or 'bot'
        
        # Load background
        self._load_background()
        
        # Keyboard input (for desktop testing only - not on mobile)
        self._keyboard = None
        self.keys_pressed = set()
        if platform not in ('android', 'ios'):
            self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
            if self._keyboard:
                self._keyboard.bind(on_key_down=self._on_key_down)
                self._keyboard.bind(on_key_up=self._on_key_up)
        
        # Bind to window size
        Window.bind(size=self.on_window_resize)
    
    def _get_scale_factor(self):
        """Calculate scale factor based on screen size."""
        base_width = 1000
        base_height = 600
        width_scale = Window.width / base_width
        height_scale = Window.height / base_height
        return min(width_scale, height_scale)
    
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
        # Health bars auto-update their positions in draw()
    
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
        
        return True
    
    def _on_key_up(self, keyboard, keycode):
        key = keycode[1]
        self.keys_pressed.discard(key)
        
        # Reset movement when keys are released
        if key == 'a':
            self.fighter_1.move_left = False
        if key == 'd':
            self.fighter_1.move_right = False
        
        return True
    
    def update(self, dt):
        """Main game loop."""
        self.screen_width = Window.width
        self.screen_height = Window.height
        
        # Apply slow motion to dt
        effective_dt = dt * self.slow_motion_factor
        
        # If game is over, only update slow motion timer and animations
        if self.game_over:
            self.game_over_timer += dt
            
            # Gradually slow down
            if self.slow_motion_factor > 0.2:
                self.slow_motion_factor -= dt * 0.8  # Slow down over ~1 second
                self.slow_motion_factor = max(0.2, self.slow_motion_factor)
            
            # Update animations in slow motion
            self.fighter_1.update_animation(self.slow_motion_factor)
            self.fighter_2.update_animation(self.slow_motion_factor)
            
            # Redraw
            self.draw_game()
            return
        
        # Handle keyboard movement for Player 1
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
        
        # Update bot AI (controls fighter 2)
        self.bot_ai.update(self.fighter_1, self.screen_width)
        
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
        if not self.fighter_1.alive and not self.game_over:
            self._trigger_game_over('bot')
        elif not self.fighter_2.alive and not self.game_over:
            self._trigger_game_over('player')
        
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
    
    def _trigger_game_over(self, winner):
        """Trigger game over state."""
        self.game_over = True
        self.game_over_timer = 0
        self.slow_motion_factor = 1.0
        self.winner = winner
        
        # Disable player movement
        self.fighter_1.move_left = False
        self.fighter_1.move_right = False
        self.fighter_2.move_left = False
        self.fighter_2.move_right = False
        
        # Stop any ongoing attacks and reset to idle (except for the dead fighter)
        if self.fighter_1.alive:
            self.fighter_1.attacking = False
            self.fighter_1.current_action = 'Idle'
            self.fighter_1.frame_index = 0
            self.fighter_1.animation_counter = 0
        if self.fighter_2.alive:
            self.fighter_2.attacking = False
            self.fighter_2.current_action = 'Idle'
            self.fighter_2.frame_index = 0
            self.fighter_2.animation_counter = 0
        
        self.keys_pressed.clear()
    
    def reset_game(self):
        """Reset the game to initial state."""
        scale = self._get_scale_factor()
        ground_y = int(GROUND_Y * scale)
        self.fighter_1.reset(int(200 * scale), ground_y)
        self.fighter_2.reset(int(self.screen_width - 300 * scale), ground_y)
        
        # Reset game over state
        self.game_over = False
        self.game_over_timer = 0
        self.slow_motion_factor = 1.0
        self.winner = None


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
        
        # Game over popup (initially hidden)
        self.game_over_popup = None
        
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
        
        # Check if we need to show game over popup
        if self.game_widget.game_over and self.game_widget.game_over_timer > 1.5 and self.game_over_popup is None:
            self._show_game_over_popup()
    
    def _show_game_over_popup(self):
        """Show the game over popup."""
        scale = self.game_widget._get_scale_factor()
        
        # Create popup container
        popup_width = int(400 * scale)
        popup_height = int(250 * scale)
        popup_x = (Window.width - popup_width) // 2
        popup_y = (Window.height - popup_height) // 2
        
        self.game_over_popup = Widget(size_hint=(None, None), size=(popup_width, popup_height), pos=(popup_x, popup_y))
        
        # Draw popup background at popup position
        with self.game_over_popup.canvas:
            Color(0, 0, 0, 0.85)
            RoundedRectangle(pos=(popup_x, popup_y), size=(popup_width, popup_height), radius=[20])
        
        # Result text
        if self.game_widget.winner == 'player':
            result_text = 'YOU WIN!'
            result_color = (0.2, 0.8, 0.2, 1)  # Green
        else:
            result_text = 'YOU LOSE'
            result_color = (0.9, 0.2, 0.2, 1)  # Red
        
        result_label = Label(
            text=result_text,
            font_size=int(48 * scale),
            color=result_color,
            bold=True,
            size_hint=(None, None),
            size=(popup_width, int(60 * scale)),
            pos=(popup_x, popup_y + popup_height - int(90 * scale))
        )
        self.game_over_popup.add_widget(result_label)
        
        # Retry button
        btn_width = int(150 * scale)
        btn_height = int(50 * scale)
        btn_spacing = int(20 * scale)
        btn_start_x = popup_x + (popup_width - btn_width * 2 - btn_spacing) // 2
        btn_y = popup_y + int(40 * scale)
        
        retry_btn = Button(
            text='RETRY',
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(btn_start_x, btn_y),
            background_color=(0.2, 0.6, 0.2, 1),
            font_size=int(24 * scale)
        )
        retry_btn.bind(on_press=self._on_retry)
        self.game_over_popup.add_widget(retry_btn)
        
        # Menu button
        menu_btn = Button(
            text='MENU',
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(btn_start_x + btn_width + btn_spacing, btn_y),
            background_color=(0.6, 0.2, 0.2, 1),
            font_size=int(24 * scale)
        )
        menu_btn.bind(on_press=self._on_menu)
        self.game_over_popup.add_widget(menu_btn)
        
        self.add_widget(self.game_over_popup)
    
    def _on_retry(self, instance):
        """Handle retry button press."""
        self._hide_game_over_popup()
        self.reset_game()
    
    def _on_menu(self, instance):
        """Handle menu button press."""
        self._hide_game_over_popup()
        self.reset_game()
        self.app.switch_screen(SCREENS['START'])
    
    def _hide_game_over_popup(self):
        """Hide and remove the game over popup."""
        if self.game_over_popup:
            self.remove_widget(self.game_over_popup)
            self.game_over_popup = None
    
    def on_pause(self, instance):
        """Handle pause button press."""
        self.app.switch_screen(SCREENS['PAUSE'])
    
    def on_window_resize(self, window, size):
        """Handle window resize."""
        self.pause_btn.pos = (size[0] // 2 - 30, size[1] - 70)
    
    def reset_game(self):
        """Reset the game."""
        self._hide_game_over_popup()
        self.game_widget.reset_game()
