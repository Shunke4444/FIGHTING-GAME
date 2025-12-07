"""
Fighter Component - The main fighter/character class
Handles animations, movement, attacks, and health with responsive scaling
"""

import os
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window

from config import (
    SPRITE_CONFIG, GROUND_Y, FIGHTER_SPEED, GRAVITY, 
    MAX_JUMPS, JUMP_VELOCITY, ATTACK_DAMAGE, ATTACK_RANGE,
    HIT_COOLDOWN, ATTACK_COOLDOWN, FRAMES_PER_ANIMATION
)


class Fighter:
    """Fighter class for game characters with responsive scaling."""
    
    # Base dimensions (for 1000x600 screen)
    BASE_RECT_WIDTH = 105
    BASE_RECT_HEIGHT = 225
    
    def __init__(self, x, y, name='fantasy_warrior', is_player_2=False):
        self.name = name
        self.flip = is_player_2
        self.is_player_2 = is_player_2
        
        # Get config
        config = SPRITE_CONFIG.get(self.name, SPRITE_CONFIG['fantasy_warrior'])
        
        # Store base dimensions
        self.base_scale_width = config['scale_width']
        self.base_scale_height = config['scale_height']
        self.base_visual_y_pull = config['visual_y_pull']
        self.death_y_adjustment = config['death_y_adj']
        self.animation_config = config['animations']
        
        # Update scaled dimensions
        self._update_scaled_dimensions()
        
        # Position and physics
        self.x = x
        self.y = y
        self.vel_y = 0
        self.jump = False
        self.jump_count = 0
        
        # Combat state
        self.attack_type = 0
        self.attacking = False
        self.attack_hit_registered = False  # Prevents multiple hits per attack
        self.health = 100
        self.hit_cooldown = 0
        self.attack_cooldown = 0
        self.alive = True
        self.death_animation_done = False
        
        # Animation state
        self.current_action = 'Idle'
        self.frame_index = 0
        self.animation_counter = 0
        self.animations = {}
        self.current_texture = None
        
        # Movement input state (for touch controls)
        self.move_left = False
        self.move_right = False
        
        # Load animations
        self.load_animations()
    
    def _get_scale_factor(self):
        """Calculate scale factor based on screen size."""
        base_width = 1000
        base_height = 600
        width_scale = Window.width / base_width
        height_scale = Window.height / base_height
        return min(width_scale, height_scale)
    
    def _update_scaled_dimensions(self):
        """Update dimensions based on current screen size."""
        scale = self._get_scale_factor()
        
        self.scale_width = int(self.base_scale_width * scale)
        self.scale_height = int(self.base_scale_height * scale)
        self.visual_y_pull = int(self.base_visual_y_pull * scale)
        
        self.RECT_WIDTH = int(self.BASE_RECT_WIDTH * scale)
        self.RECT_HEIGHT = int(self.BASE_RECT_HEIGHT * scale)
        
        self.x_offset = (self.scale_width - self.RECT_WIDTH) // 2
    
    def load_animations(self):
        """Load sprite sheet animations."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        for action, num_frames in self.animation_config.items():
            self.animations[action] = []
            
            if self.name == 'knight':
                file_path = os.path.join(base_path, f'assets/images/characters/knight/{action}.png')
            else:
                file_path = os.path.join(base_path, f'assets/images/characters/fantasy_warrior/{action}.png')
            
            try:
                if os.path.exists(file_path):
                    core_img = CoreImage(file_path)
                    texture = core_img.texture
                    
                    frame_width = texture.width // num_frames
                    frame_height = texture.height
                    
                    for frame_idx in range(num_frames):
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
        
        # Set initial texture
        if 'Idle' in self.animations and self.animations['Idle']:
            self.current_texture = self.animations['Idle'][0]
    
    def update_animation(self, slow_motion_factor=1.0):
        """Update animation frame with optional slow motion."""
        if self.current_action not in self.animations:
            return
        if len(self.animations[self.current_action]) == 0:
            return
        
        if self.current_action == 'Death' and self.death_animation_done:
            return
        
        # Apply slow motion to animation speed
        self.animation_counter += slow_motion_factor
        
        if self.animation_counter >= FRAMES_PER_ANIMATION:
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
                    self.attack_cooldown = ATTACK_COOLDOWN
        
        if self.current_action in self.animations:
            frames = self.animations[self.current_action]
            if len(frames) > 0:
                safe_index = min(self.frame_index, len(frames) - 1)
                self.current_texture = frames[safe_index]
    
    def move(self, screen_width, screen_height, target):
        """Update fighter position and state."""
        # Update scaled dimensions for responsive sizing
        self._update_scaled_dimensions()
        
        # Get scaled physics values
        scale = self._get_scale_factor()
        speed = FIGHTER_SPEED * scale
        gravity = GRAVITY * scale
        ground_y = int(GROUND_Y * scale)
        
        dx = 0
        dy = 0
        
        # Check if health depleted
        if self.health <= 0:
            self.health = 0
            self.alive = False
            if self.current_action != 'Death':
                self.current_action = 'Death'
                self.frame_index = 0
                self.animation_counter = 0
            
            self.vel_y -= gravity
            dy = self.vel_y
            if self.y + dy < ground_y:
                self.vel_y = 0
                dy = ground_y - self.y
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
                dx = -speed
                self.flip = True
                is_running = True
            if self.move_right:
                dx = speed
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
        
        # Apply gravity
        self.vel_y -= gravity
        dy = self.vel_y
        
        # Horizontal boundaries
        if self.x + dx < 0:
            dx = -self.x
        if self.x + self.RECT_WIDTH + dx > screen_width:
            dx = screen_width - self.x - self.RECT_WIDTH
        
        # Ground collision
        if self.y + dy < ground_y:
            self.vel_y = 0
            self.jump_count = 0
            self.jump = False
            dy = ground_y - self.y
        else:
            self.jump = True
        
        self.x += dx
        self.y += dy
    
    def do_jump(self):
        """Trigger jump."""
        if not self.attacking and self.jump_count < MAX_JUMPS:
            scale = self._get_scale_factor()
            self.vel_y = JUMP_VELOCITY * scale
            self.jump_count += 1
    
    def do_attack(self, attack_type):
        """Trigger attack."""
        if not self.attacking and self.attack_cooldown == 0 and self.alive:
            self.attacking = True
            self.attack_hit_registered = False  # Reset for new attack
            self.attack_type = attack_type
            self.current_action = f'Attack{attack_type}'
            self.frame_index = 0
            self.animation_counter = 0
    
    def check_attack_hit(self, target):
        """Check if attack hits target - only deals damage at the impact frame."""
        if not self.attacking or not self.alive:
            return
        
        # Already hit with this attack
        if self.attack_hit_registered:
            return
        
        # Get the total frames for current attack animation
        action = self.current_action
        if action not in self.animations or len(self.animations[action]) == 0:
            return
        
        total_frames = len(self.animations[action])
        
        # Calculate the impact frame (around 40% through the animation)
        # This is when the slash starts to connect
        impact_frame = int(total_frames * 0.4)
        
        # Only check for hit at the impact frame
        if self.frame_index != impact_frame:
            return
        
        # Scaled attack range
        scale = self._get_scale_factor()
        attack_range = int(ATTACK_RANGE * scale)
        
        # Create attack hitbox
        if self.flip:
            attack_x = self.x - attack_range
        else:
            attack_x = self.x + self.RECT_WIDTH
        
        # Rectangle collision
        if (attack_x < target.x + target.RECT_WIDTH and
            attack_x + attack_range > target.x and
            self.y < target.y + target.RECT_HEIGHT and
            self.y + self.RECT_HEIGHT > target.y):
            
            if target.hit_cooldown == 0:
                damage = ATTACK_DAMAGE.get(self.attack_type, 15)
                target.health -= damage
                target.hit_cooldown = HIT_COOLDOWN
                self.attack_hit_registered = True  # Mark this attack as having hit
    
    def get_draw_pos(self):
        """Get position to draw sprite."""
        draw_x = self.x - self.x_offset
        draw_y = self.y - self.visual_y_pull
        
        if self.current_action == 'Death':
            draw_y += self.death_y_adjustment
        
        return draw_x, draw_y
    
    def reset(self, x, y):
        """Reset fighter to initial state."""
        self.x = x
        self.y = y
        self.vel_y = 0
        self.jump = False
        self.jump_count = 0
        self.attack_type = 0
        self.attacking = False
        self.attack_hit_registered = False
        self.health = 100
        self.hit_cooldown = 0
        self.attack_cooldown = 0
        self.alive = True
        self.death_animation_done = False
        self.current_action = 'Idle'
        self.frame_index = 0
        self.animation_counter = 0
        self.move_left = False
        self.move_right = False
        
        if 'Idle' in self.animations and self.animations['Idle']:
            self.current_texture = self.animations['Idle'][0]
