"""
Fighting Game - Kivy Mobile Version
This version can be compiled to APK using Buildozer
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
import os

# Set window size for desktop testing (will be fullscreen on mobile)
Window.size = (1000, 600)

# Sprite configurations
SPRITE_CONFIG = {
    'fantasy_warrior': {
        'scale_width': 350,
        'scale_height': 550,
        'visual_y_pull': 120,
        'death_y_adj': 30,
        'animations': {
            'Idle': 10,
            'Run': 8,
            'Jump': 3,
            'Attack1': 7,
            'Attack2': 7,
            'Attack3': 8,
            'Take hit': 3,
            'Death': 7
        }
    },
    'knight': {
        'scale_width': 350,
        'scale_height': 420,
        'visual_y_pull': 0,
        'death_y_adj': 30,
        'animations': {
            'Idle': 10,
            'Run': 10,
            'Jump': 3,
            'Attack1': 4,
            'Attack2': 6,
            'Attack3': 10,
            'hit': 1,
            'Death': 10
        }
    }
}


class Fighter:
    """Fighter class adapted for Kivy"""
    
    RECT_WIDTH = 105
    RECT_HEIGHT = 225
    
    def __init__(self, x, y, name='fantasy_warrior', is_player_2=False):
        self.name = name
        self.flip = is_player_2
        self.is_player_2 = is_player_2
        
        # Get config
        config = SPRITE_CONFIG.get(self.name, SPRITE_CONFIG['fantasy_warrior'])
        
        self.scale_width = config['scale_width']
        self.scale_height = config['scale_height']
        self.visual_y_pull = config['visual_y_pull']
        self.death_y_adjustment = config['death_y_adj']
        self.animation_config = config['animations']
        
        self.x_offset = (self.scale_width - self.RECT_WIDTH) // 2
        
        # Position and hitbox
        self.x = x
        self.y = y
        self.vel_y = 0
        self.jump = False
        self.jump_count = 0
        self.max_jumps = 2
        self.attack_type = 0
        self.attacking = False
        self.health = 100
        self.hit_cooldown = 0
        self.attack_cooldown = 0
        self.alive = True
        self.death_animation_done = False
        
        self.current_action = 'Idle'
        self.frame_index = 0
        self.animation_counter = 0
        self.animations = {}
        
        # Movement input state (for touch controls)
        self.move_left = False
        self.move_right = False
        
        # Load animations
        self.load_animations()
    
    def load_animations(self):
        """Load sprite sheet animations"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        for action, num_frames in self.animation_config.items():
            self.animations[action] = []
            
            if self.name == 'knight':
                file_path = os.path.join(base_path, f'assets/images/characters/knight/{action}.png')
            else:
                file_path = os.path.join(base_path, f'assets/images/characters/fantasy_warrior/{action}.png')
            
            try:
                # Load the sprite sheet using Kivy's CoreImage
                if os.path.exists(file_path):
                    core_img = CoreImage(file_path)
                    texture = core_img.texture
                    
                    frame_width = texture.width // num_frames
                    frame_height = texture.height
                    
                    for frame_idx in range(num_frames):
                        # Extract frame region from sprite sheet
                        # Kivy textures have origin at bottom-left
                        frame_texture = texture.get_region(
                            frame_idx * frame_width,
                            0,
                            frame_width,
                            frame_height
                        )
                        self.animations[action].append(frame_texture)
                else:
                    print(f"Warning: Could not find {file_path}")
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")
        
        # Set initial image
        if 'Idle' in self.animations and self.animations['Idle']:
            self.current_texture = self.animations['Idle'][0]
        else:
            self.current_texture = None
    
    def update_animation(self):
        """Update animation frame"""
        if self.current_action not in self.animations or len(self.animations[self.current_action]) == 0:
            return
        
        if self.current_action == 'Death' and self.death_animation_done:
            return
        
        self.animation_counter += 1
        frames_per_frame = 5
        
        if self.animation_counter >= frames_per_frame:
            self.animation_counter = 0
            self.frame_index += 1
            
            max_frames = len(self.animations[self.current_action])
            
            if self.frame_index >= max_frames:
                if self.current_action == 'Death':
                    self.frame_index = max_frames - 1
                    self.death_animation_done = True
                else:
                    self.frame_index = 0
                
                if self.current_action in ['Attack1', 'Attack2', 'Attack3']:
                    self.attacking = False
                    self.attack_cooldown = 20
        
        if self.current_action in self.animations and len(self.animations[self.current_action]) > 0:
            safe_index = min(self.frame_index, len(self.animations[self.current_action]) - 1)
            self.current_texture = self.animations[self.current_action][safe_index]
    
    def move(self, screen_width, screen_height, target):
        """Update fighter position and state"""
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        
        # Ground level (from bottom of screen)
        GROUND_Y = 110
        
        # Check if health depleted
        if self.health <= 0:
            self.health = 0
            self.alive = False
            if self.current_action != 'Death':
                self.current_action = 'Death'
                self.frame_index = 0
                self.animation_counter = 0
            
            self.vel_y -= GRAVITY  # Kivy Y is inverted
            dy = self.vel_y
            if self.y + dy < GROUND_Y:
                self.vel_y = 0
                dy = GROUND_Y - self.y
            self.y += dy
            return
        
        # Decrease cooldowns
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        is_running = False
        
        if not self.attacking:
            if self.move_left:
                dx = -SPEED
                self.flip = True
                is_running = True
            if self.move_right:
                dx = SPEED
                self.flip = False
                is_running = True
            
            # Update action based on state
            if self.vel_y > 0 or (self.vel_y < 0 and self.jump):
                if self.current_action != 'Jump':
                    self.frame_index = 0
                    self.animation_counter = 0
                self.current_action = 'Jump'
            elif is_running:
                self.current_action = 'Run'
            else:
                self.current_action = 'Idle'
        
        # Apply gravity (Kivy Y is inverted - positive is up)
        self.vel_y -= GRAVITY
        dy = self.vel_y
        
        # Horizontal boundaries
        if self.x + dx < 0:
            dx = -self.x
        if self.x + self.RECT_WIDTH + dx > screen_width:
            dx = screen_width - self.x - self.RECT_WIDTH
        
        # Ground collision
        if self.y + dy < GROUND_Y:
            self.vel_y = 0
            self.jump_count = 0
            self.jump = False
            dy = GROUND_Y - self.y
        else:
            self.jump = True
        
        self.x += dx
        self.y += dy
    
    def do_jump(self):
        """Trigger jump"""
        if not self.attacking and self.jump_count < self.max_jumps:
            self.vel_y = 30  # Positive because Kivy Y goes up
            self.jump_count += 1
    
    def do_attack(self, attack_type):
        """Trigger attack"""
        if not self.attacking and self.attack_cooldown == 0 and self.alive:
            self.attacking = True
            self.attack_type = attack_type
            self.current_action = f'Attack{attack_type}'
            self.frame_index = 0
            self.animation_counter = 0
    
    def check_attack_hit(self, target):
        """Check if attack hits target"""
        if not self.attacking or not self.alive:
            return
        
        attack_range = 80
        
        # Create attack hitbox
        if self.flip:
            attack_x = self.x - attack_range
        else:
            attack_x = self.x + self.RECT_WIDTH
        
        # Simple rectangle collision
        if (attack_x < target.x + target.RECT_WIDTH and
            attack_x + attack_range > target.x and
            self.y < target.y + target.RECT_HEIGHT and
            self.y + self.RECT_HEIGHT > target.y):
            
            if target.hit_cooldown == 0:
                if self.attack_type == 1:
                    damage = 15
                elif self.attack_type == 2:
                    damage = 20
                else:
                    damage = 35
                target.health -= damage
                target.hit_cooldown = 30
    
    def get_draw_pos(self):
        """Get position to draw sprite"""
        draw_x = self.x - self.x_offset
        draw_y = self.y - self.visual_y_pull
        
        if self.current_action == 'Death':
            draw_y += self.death_y_adjustment
        
        return draw_x, draw_y


class TouchButton(Button):
    """Custom touch button for mobile controls"""
    
    def __init__(self, player, action, **kwargs):
        super().__init__(**kwargs)
        self.player = player  # 1 or 2
        self.action = action
        self.background_color = (0.3, 0.3, 0.3, 0.7)
        self.font_size = 24
        self.pressed = False
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = True
            self.background_color = (0.5, 0.5, 0.5, 0.9)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.pressed:
            self.pressed = False
            self.background_color = (0.3, 0.3, 0.3, 0.7)
            return True
        return super().on_touch_up(touch)


class GameWidget(Widget):
    """Main game widget"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.screen_width = Window.width
        self.screen_height = Window.height
        
        # Calculate ground Y position
        GROUND_Y = 110
        fighter_start_y = GROUND_Y
        
        # Create fighters
        self.fighter_1 = Fighter(200, fighter_start_y, 'fantasy_warrior', is_player_2=False)
        self.fighter_2 = Fighter(self.screen_width - 300, fighter_start_y, 'knight', is_player_2=True)
        
        # Load background
        base_path = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_path, 'assets/images/backgrounds/FOREST.png')
        
        try:
            self.bg_texture = CoreImage(bg_path).texture
        except:
            self.bg_texture = None
            print(f"Warning: Could not load background from {bg_path}")
        
        # Keyboard input
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        
        # Track pressed keys
        self.keys_pressed = set()
        
        # Start game loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)
    
    def _on_keyboard_closed(self):
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
        """Main game loop"""
        self.screen_width = Window.width
        self.screen_height = Window.height
        
        # Handle keyboard movement for Player 1
        self.fighter_1.move_left = 'a' in self.keys_pressed
        self.fighter_1.move_right = 'd' in self.keys_pressed
        
        # Handle keyboard attacks for Player 1
        if 'j' in self.keys_pressed and 'k' in self.keys_pressed:
            self.fighter_1.do_attack(3)
        elif 'j' in self.keys_pressed:
            self.fighter_1.do_attack(1)
        elif 'k' in self.keys_pressed:
            self.fighter_1.do_attack(2)
        
        # Handle keyboard movement for Player 2
        self.fighter_2.move_left = 'left' in self.keys_pressed
        self.fighter_2.move_right = 'right' in self.keys_pressed
        
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
        
        # Redraw
        self.draw_game()
    
    def draw_game(self):
        """Draw the game"""
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
            self.draw_health_bar(self.fighter_1.health, 20, self.screen_height - 50)
            self.draw_health_bar(self.fighter_2.health, self.screen_width - 320, self.screen_height - 50)
            
            # Draw fighters
            self.draw_fighter(self.fighter_1)
            self.draw_fighter(self.fighter_2)
    
    def draw_health_bar(self, health, x, y):
        """Draw a health bar"""
        with self.canvas:
            # Background (red)
            Color(1, 0, 0, 1)
            Rectangle(pos=(x, y), size=(300, 30))
            
            # Health (green)
            Color(0, 1, 0, 1)
            ratio = max(0, health / 100)
            Rectangle(pos=(x, y), size=(300 * ratio, 30))
            
            # Border
            Color(1, 1, 1, 1)
            from kivy.graphics import Line
            Line(rectangle=(x, y, 300, 30), width=2)
    
    def draw_fighter(self, fighter):
        """Draw a fighter"""
        if fighter.current_texture is None:
            return
        
        draw_x, draw_y = fighter.get_draw_pos()
        
        with self.canvas:
            Color(1, 1, 1, 1)
            
            texture = fighter.current_texture
            
            # Handle flip
            if fighter.flip:
                # For flipped sprites, we need to flip the texture
                texture = texture.get_region(0, 0, texture.width, texture.height)
                texture.flip_horizontal()
            
            Rectangle(
                texture=texture,
                pos=(draw_x, draw_y),
                size=(fighter.scale_width, fighter.scale_height)
            )


class FightingGameApp(App):
    """Main Kivy application"""
    
    def build(self):
        # Create main layout
        layout = FloatLayout()
        
        # Add game widget
        self.game = GameWidget()
        layout.add_widget(self.game)
        
        # Add mobile touch controls
        self.add_touch_controls(layout)
        
        return layout
    
    def add_touch_controls(self, layout):
        """Add touch controls for mobile"""
        btn_size = (80, 80)
        
        # Player 1 controls (left side)
        # Left button
        p1_left = Button(
            text='←',
            size_hint=(None, None),
            size=btn_size,
            pos=(20, 100),
            background_color=(0.3, 0.3, 0.8, 0.7),
            font_size=32
        )
        p1_left.bind(on_touch_down=lambda btn, touch: self.on_move_touch(btn, touch, self.game.fighter_1, 'left', True))
        p1_left.bind(on_touch_up=lambda btn, touch: self.on_move_touch(btn, touch, self.game.fighter_1, 'left', False))
        layout.add_widget(p1_left)
        
        # Right button
        p1_right = Button(
            text='→',
            size_hint=(None, None),
            size=btn_size,
            pos=(120, 100),
            background_color=(0.3, 0.3, 0.8, 0.7),
            font_size=32
        )
        p1_right.bind(on_touch_down=lambda btn, touch: self.on_move_touch(btn, touch, self.game.fighter_1, 'right', True))
        p1_right.bind(on_touch_up=lambda btn, touch: self.on_move_touch(btn, touch, self.game.fighter_1, 'right', False))
        layout.add_widget(p1_right)
        
        # Jump button
        p1_jump = Button(
            text='↑',
            size_hint=(None, None),
            size=btn_size,
            pos=(70, 190),
            background_color=(0.3, 0.8, 0.3, 0.7),
            font_size=32
        )
        p1_jump.bind(on_press=lambda btn: self.game.fighter_1.do_jump())
        layout.add_widget(p1_jump)
        
        # Attack 1
        p1_atk1 = Button(
            text='A1',
            size_hint=(None, None),
            size=btn_size,
            pos=(20, 10),
            background_color=(0.8, 0.3, 0.3, 0.7),
            font_size=24
        )
        p1_atk1.bind(on_press=lambda btn: self.game.fighter_1.do_attack(1))
        layout.add_widget(p1_atk1)
        
        # Attack 2
        p1_atk2 = Button(
            text='A2',
            size_hint=(None, None),
            size=btn_size,
            pos=(120, 10),
            background_color=(0.8, 0.3, 0.3, 0.7),
            font_size=24
        )
        p1_atk2.bind(on_press=lambda btn: self.game.fighter_1.do_attack(2))
        layout.add_widget(p1_atk2)
        
        # Player 2 controls (right side)
        base_x = Window.width - 200
        
        # Left button
        p2_left = Button(
            text='←',
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'right': 0.85},
            pos=(base_x, 100),
            background_color=(0.8, 0.6, 0.3, 0.7),
            font_size=32
        )
        p2_left.bind(on_touch_down=lambda btn, touch: self.on_move_touch(btn, touch, self.game.fighter_2, 'left', True))
        p2_left.bind(on_touch_up=lambda btn, touch: self.on_move_touch(btn, touch, self.game.fighter_2, 'left', False))
        layout.add_widget(p2_left)
        
        # Right button
        p2_right = Button(
            text='→',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x + 100, 100),
            background_color=(0.8, 0.6, 0.3, 0.7),
            font_size=32
        )
        p2_right.bind(on_touch_down=lambda btn, touch: self.on_move_touch(btn, touch, self.game.fighter_2, 'right', True))
        p2_right.bind(on_touch_up=lambda btn, touch: self.on_move_touch(btn, touch, self.game.fighter_2, 'right', False))
        layout.add_widget(p2_right)
        
        # Jump button
        p2_jump = Button(
            text='↑',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x + 50, 190),
            background_color=(0.3, 0.8, 0.3, 0.7),
            font_size=32
        )
        p2_jump.bind(on_press=lambda btn: self.game.fighter_2.do_jump())
        layout.add_widget(p2_jump)
        
        # Attack 1
        p2_atk1 = Button(
            text='A1',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x, 10),
            background_color=(0.8, 0.5, 0.3, 0.7),
            font_size=24
        )
        p2_atk1.bind(on_press=lambda btn: self.game.fighter_2.do_attack(1))
        layout.add_widget(p2_atk1)
        
        # Attack 2
        p2_atk2 = Button(
            text='A2',
            size_hint=(None, None),
            size=btn_size,
            pos=(base_x + 100, 10),
            background_color=(0.8, 0.5, 0.3, 0.7),
            font_size=24
        )
        p2_atk2.bind(on_press=lambda btn: self.game.fighter_2.do_attack(2))
        layout.add_widget(p2_atk2)
        
        # Player labels
        p1_label = Label(
            text='P1',
            pos=(70, 280),
            size_hint=(None, None),
            font_size=20,
            color=(0.3, 0.3, 1, 1)
        )
        layout.add_widget(p1_label)
        
        p2_label = Label(
            text='P2',
            pos=(base_x + 50, 280),
            size_hint=(None, None),
            font_size=20,
            color=(1, 0.6, 0.3, 1)
        )
        layout.add_widget(p2_label)
    
    def on_move_touch(self, btn, touch, fighter, direction, pressed):
        """Handle movement button touch"""
        if btn.collide_point(*touch.pos):
            if direction == 'left':
                fighter.move_left = pressed
            elif direction == 'right':
                fighter.move_right = pressed
            return True
        return False


if __name__ == '__main__':
    FightingGameApp().run()
