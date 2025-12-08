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
from kivy.core.audio import SoundLoader
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
        self.bot_ai = BotAI(self.fighter_2, difficulty='hard')
        
        # Create health bars (now auto-scaling)
        self.health_bar_1 = HealthBar(is_flipped=False)
        self.health_bar_2 = HealthBar(is_flipped=True)
        
        # Game over state
        self.game_over = False
        self.game_over_timer = 0
        self.slow_motion_factor = 1.0
        self.winner = None  # 'player' or 'bot'
        
        # Match timer (40 seconds)
        self.match_time = 40.0
        
        # Countdown state (3, 2, 1, FIGHT!)
        self.countdown_active = True
        self.countdown_time = 1.9  # Total countdown duration
        self.countdown_text = "3"
        
        # Load background
        self._load_background()
        
        # Keyboard input (for desktop testing only - not on mobile)
        self._keyboard = None
        self.keys_pressed = set()
        self._setup_keyboard()
        
        # Bind to window size
        Window.bind(size=self.on_window_resize)
    
    def _setup_keyboard(self):
        """Setup keyboard input for desktop."""
        if platform not in ('android', 'ios'):
            if self._keyboard:
                self._keyboard.unbind(on_key_down=self._on_key_down)
                self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
            if self._keyboard:
                self._keyboard.bind(on_key_down=self._on_key_down)
                self._keyboard.bind(on_key_up=self._on_key_up)
    
    def _release_keyboard(self):
        """Release keyboard input."""
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard.release()
            self._keyboard = None
        self.keys_pressed.clear()
    
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
        
        # Player 1 Dodge
        if key == 'spacebar':
            self.fighter_1.do_dodge()
        
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
        
        # Handle countdown
        if self.countdown_active:
            self.countdown_time -= dt
            
            # Determine countdown text based on remaining time
            # 1.9 -> 1.425: "3", 1.425 -> 0.95: "2", 0.95 -> 0.475: "1", 0.475 -> 0: "FIGHT!"
            if self.countdown_time > 1.425:
                self.countdown_text = "3"
            elif self.countdown_time > 0.95:
                self.countdown_text = "2"
            elif self.countdown_time > 0.475:
                self.countdown_text = "1"
            elif self.countdown_time > 0:
                self.countdown_text = "FIGHT!"
            else:
                self.countdown_active = False
                self.countdown_text = ""
            
            # During countdown, just draw the game (fighters idle)
            self.fighter_1.update_animation()
            self.fighter_2.update_animation()
            self.draw_game()
            return
        
        # Apply slow motion to dt
        effective_dt = dt * self.slow_motion_factor
        
        # If game is over, only update slow motion timer and animations
        if self.game_over:
            self.game_over_timer += dt
            
            # Gradually slow down
            if self.slow_motion_factor > 0.2:
                self.slow_motion_factor -= dt * 0.8  # Slow down over ~1 second
                self.slow_motion_factor = max(0.2, self.slow_motion_factor)
            
            # Continue applying gravity so fighters land on the ground
            self.fighter_1.move(self.screen_width, self.screen_height, self.fighter_2)
            self.fighter_2.move(self.screen_width, self.screen_height, self.fighter_1)
            
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
        # K (Attack 2) while moving triggers Attack 3
        if 'k' in self.keys_pressed and ('a' in self.keys_pressed or 'd' in self.keys_pressed):
            self.fighter_1.do_attack(3)  # Directional combo attack!
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
        
        # Update match timer
        self.match_time -= dt
        if self.match_time <= 0:
            self.match_time = 0
            # Determine winner by health
            if self.fighter_1.health > self.fighter_2.health:
                self._trigger_game_over('player')
            elif self.fighter_2.health > self.fighter_1.health:
                self._trigger_game_over('bot')
            else:
                # Tie - bot wins by default
                self._trigger_game_over('bot')
        
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
        
        # Draw countdown text if active
        if self.countdown_active and self.countdown_text:
            self._draw_countdown()
    
    def _draw_countdown(self):
        """Draw the countdown text in the center of the screen."""
        from kivy.core.text import Label as CoreLabel
        
        # Create label with large font
        font_size = 120 if self.countdown_text != "FIGHT!" else 100
        label = CoreLabel(
            text=self.countdown_text,
            font_size=font_size,
            bold=True
        )
        label.refresh()
        
        # Get texture from label
        texture = label.texture
        
        # Calculate center position
        center_x = self.screen_width // 2 - texture.width // 2
        center_y = self.screen_height // 2 - texture.height // 2
        
        with self.canvas:
            # Draw semi-transparent background for better visibility
            Color(0, 0, 0, 0.5)
            RoundedRectangle(
                pos=(center_x - 20, center_y - 10),
                size=(texture.width + 40, texture.height + 20),
                radius=[15]
            )
            
            # Draw text with color based on countdown
            if self.countdown_text == "FIGHT!":
                Color(1, 0.3, 0.3, 1)  # Red for FIGHT
            else:
                Color(1, 1, 1, 1)  # White for numbers
            
            Rectangle(texture=texture, pos=(center_x, center_y), size=texture.size)
    
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
        
        # Reset match timer
        self.match_time = 40.0
        
        # Reset countdown
        self.countdown_active = True
        self.countdown_time = 1.9
        self.countdown_text = "3"


class GameScreen(BaseScreen):
    """The main game screen."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Get settings for audio
        from utils.settings import SettingsManager
        self.settings = SettingsManager.get_instance()
        
        # Load background music
        self.bg_music = None
        self._load_background_music()
        
        # Create game widget
        self.game_widget = GameWidget(size_hint=(1, 1))
        self.add_widget(self.game_widget)
        
        # Create touch controls
        self.touch_controls = TouchControls(self.game_widget)
        self.touch_controls.create_controls(self)
        
        # Create timer label at top center
        self.timer_label = Label(
            text='60',
            size_hint=(None, None),
            size=(80, 50),
            pos=(Window.width // 2 - 40, Window.height - 50),
            font_size=36,
            bold=True,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=2
        )
        self.add_widget(self.timer_label)
        
        # Create pause button below timer
        self.pause_btn = Button(
            text='||',
            size_hint=(None, None),
            size=(60, 60),
            pos=(Window.width // 2 - 30, Window.height - 105),
            background_color=(0.5, 0.5, 0.5, 0.7),
            font_size=28
        )
        self.pause_btn.bind(on_press=self.on_pause)
        self.add_widget(self.pause_btn)
        
        # Game over popup (initially hidden)
        self.game_over_popup = None
        
        # Game loop event
        self.game_event = None
        
        # Music fade state
        self.music_fading = False
        self.music_fade_duration = 2.0  # Fade over 2 seconds
        self.music_fade_timer = 0.0
        self.music_original_volume = self.settings.get_music_volume()
    
    def on_enter(self):
        """Start the game loop when entering."""
        # Refresh touch controls to apply any settings changes
        self.touch_controls.reposition_controls()
        # Re-setup keyboard input
        self.game_widget._setup_keyboard()
        self.game_event = Clock.schedule_interval(self.update, 1.0 / FPS)
        # Apply saved audio settings
        sfx_volume = self.settings.get_sfx_volume()
        self.apply_sfx_volume(sfx_volume)
        # Start background music
        self.play_music()
    
    def on_leave(self):
        """Stop the game loop when leaving."""
        if self.game_event:
            self.game_event.cancel()
            self.game_event = None
        # Release keyboard when leaving
        self.game_widget._release_keyboard()
    
    def update(self, dt):
        """Update the game."""
        self.game_widget.update(dt)
        
        # Start music fade when game over begins
        if self.game_widget.game_over and not self.music_fading and self.bg_music:
            self.music_fading = True
            self.music_fade_timer = 0.0
        
        # Handle music fade out
        if self.music_fading and self.bg_music:
            self.music_fade_timer += dt
            fade_progress = min(self.music_fade_timer / self.music_fade_duration, 1.0)
            self.bg_music.volume = self.music_original_volume * (1.0 - fade_progress)
            
            # Stop music completely when fade is done
            if fade_progress >= 1.0:
                self.bg_music.stop()
                self.music_fading = False
        
        # Update timer and pause button positions for dynamic scaling
        self.timer_label.pos = (Window.width // 2 - 40, Window.height - 50)
        self.pause_btn.pos = (Window.width // 2 - 30, Window.height - 105)
        
        # Update timer display (just seconds)
        match_time = self.game_widget.match_time
        seconds = int(match_time)
        self.timer_label.text = str(seconds)
        
        # Change timer color when low
        if match_time <= 10:
            self.timer_label.color = (1, 0.2, 0.2, 1)  # Red when low
        else:
            self.timer_label.color = (1, 1, 1, 1)
        
        # Check if we need to show game over popup
        if self.game_widget.game_over and self.game_widget.game_over_timer > 3.0 and self.game_over_popup is None:
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
        self.stop_music()
        self.app.switch_screen(SCREENS['START'])
    
    def _hide_game_over_popup(self):
        """Hide and remove the game over popup."""
        if self.game_over_popup:
            self.remove_widget(self.game_over_popup)
            self.game_over_popup = None
    
    def on_pause(self, instance):
        """Handle pause button press."""
        self.pause_music()
        self.app.switch_screen(SCREENS['PAUSE'])
    
    def _load_background_music(self):
        """Load the background music."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Prefer a packaged WAV/OGG file where available; fall back to MP3
        wav_path = os.path.join(base_path, 'assets', 'images', 'sound_effects',
                                'background_music', 'Limbus_Company_Middle_Finger_Toujou.wav')
        mp3_path = os.path.join(base_path, 'assets', 'images', 'sound_effects',
                                'background_music', 'Limbus Company - Middle Finger Toujou.mp3')

        chosen_path = None
        if os.path.exists(wav_path):
            chosen_path = wav_path
        elif os.path.exists(mp3_path):
            chosen_path = mp3_path

        if chosen_path:
            self.bg_music = SoundLoader.load(chosen_path)
            if self.bg_music:
                self.bg_music.loop = True
                # Use saved volume setting
                volume = self.settings.get_music_volume()
                self.bg_music.volume = volume
                self.music_original_volume = volume
    
    def play_music(self):
        """Start playing background music."""
        if self.bg_music and self.bg_music.state != 'play':
            # Ensure volume is set from settings
            volume = self.settings.get_music_volume()
            self.bg_music.volume = volume
            self.music_original_volume = volume
            self.bg_music.play()
    
    def pause_music(self):
        """Pause background music."""
        if self.bg_music and self.bg_music.state == 'play':
            self.bg_music.stop()
    
    def stop_music(self):
        """Stop background music completely."""
        if self.bg_music:
            self.bg_music.stop()
    
    def apply_sfx_volume(self, volume):
        """Apply SFX volume to all fighter sounds."""
        # Apply to fighter 1
        fighter1 = self.game_widget.fighter_1
        for sound in fighter1.sounds.values():
            if sound:
                sound.volume = volume
        for sound in fighter1.footstep_sounds:
            if sound:
                sound.volume = volume
        
        # Apply to fighter 2
        fighter2 = self.game_widget.fighter_2
        for sound in fighter2.sounds.values():
            if sound:
                sound.volume = volume
        for sound in fighter2.footstep_sounds:
            if sound:
                sound.volume = volume
    
    def on_window_resize(self, window, size):
        """Handle window resize."""
        self.pause_btn.pos = (size[0] // 2 - 30, size[1] - 70)
    
    def reset_game(self):
        """Reset the game."""
        self._hide_game_over_popup()
        self.game_widget.reset_game()
        
        # Reset music fade state and restart music
        self.music_fading = False
        self.music_fade_timer = 0.0
        if self.bg_music:
            self.bg_music.volume = self.music_original_volume
            self.play_music()
    
    def set_difficulty(self, difficulty):
        """Set the bot difficulty."""
        self.game_widget.bot_ai.difficulty = difficulty
        self.game_widget.bot_ai._setup_difficulty()
        self.game_widget.bot_ai.decision_interval = self.game_widget.bot_ai._get_decision_interval()
