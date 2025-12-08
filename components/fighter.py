"""
Fighter Component - The main fighter/character class
Handles animations, movement, attacks, and health with responsive scaling
"""

import os
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
from kivy.core.window import Window

from config import (
    SPRITE_CONFIG, GROUND_Y, FIGHTER_SPEED, GRAVITY, 
    MAX_JUMPS, JUMP_VELOCITY, ATTACK_DAMAGE, ATTACK_RANGE,
    HIT_COOLDOWN, ATTACK_COOLDOWN, FRAMES_PER_ANIMATION,
    DODGE_COOLDOWN, DODGE_DISTANCE, DODGE_DURATION
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
        self.attack_hits_registered = set()  # Track which hit frames have connected
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
        
        # Dodge state
        self.dodging = False
        self.dodge_cooldown = 0
        self.dodge_timer = 0
        self.dodge_direction = 1  # 1 = right, -1 = left
        
        # Sound state
        self.sounds = {}
        self.footstep_sounds = []
        self.footstep_index = 0
        self.last_run_frame = -1
        self.attack3_second_swing_played = False
        
        # Load animations
        self.load_animations()
        
        # Load sounds
        self.load_sounds()
    
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
    
    def load_sounds(self):
        """Load sound effects for the fighter."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sfx_path = os.path.join(base_path, 'assets', 'images', 'sound effects')
        
        def load_sound(file_path):
            """Load a sound using Kivy's SoundLoader."""
            if not os.path.exists(file_path):
                return None
            
            try:
                sound = SoundLoader.load(file_path)
                return sound
            except Exception as e:
                print(f"[Sound] Error loading {file_path}: {e}")
                return None
        
        # Load footstep sounds
        dirt_path = os.path.join(sfx_path, 'Footsteps', 'Dirt')
        
        for i in range(1, 6):
            sound_file = os.path.join(dirt_path, f'Dirt Run {i}.wav')
            sound = load_sound(sound_file)
            if sound:
                sound.volume = 0.3
                self.footstep_sounds.append(sound)
        
        # Load jump and land sounds
        jump_file = os.path.join(dirt_path, 'Dirt Jump.wav')
        land_file = os.path.join(dirt_path, 'Dirt Land.wav')
        
        self.sounds['jump'] = load_sound(jump_file)
        if self.sounds['jump']:
            self.sounds['jump'].volume = 0.4
        
        self.sounds['land'] = load_sound(land_file)
        if self.sounds['land']:
            self.sounds['land'].volume = 0.4
        
        # Load sword attack sounds
        sword_path = os.path.join(sfx_path, 'Sword Attacks Hits and Blocks')
        
        sword_files = {
            'sword1': os.path.join(sword_path, 'Sword Attack 1.wav'),
            'sword2': os.path.join(sword_path, 'Sword Attack 2.wav'),
            'sword3': os.path.join(sword_path, 'Sword Attack 3.wav'),
        }
        
        for key, file_path in sword_files.items():
            sound = load_sound(file_path)
            if sound:
                sound.volume = 0.5
                self.sounds[key] = sound
        
        # Map attacks to sounds based on character
        # Fantasy Warrior: Attack1->Sword2, Attack2->Sword3, Attack3->Sword1
        # Knight: Attack1->Sword3, Attack2->Sword2, Attack3->Sword3+Sword2
        if self.name == 'fantasy_warrior':
            self.sounds['attack1'] = self.sounds.get('sword2')
            self.sounds['attack2'] = self.sounds.get('sword3')
            self.sounds['attack3'] = self.sounds.get('sword1')
        else:  # knight
            self.sounds['attack1'] = self.sounds.get('sword3')
            self.sounds['attack2'] = self.sounds.get('sword2')
            self.sounds['attack3_first'] = self.sounds.get('sword3')
            self.sounds['attack3_second'] = self.sounds.get('sword2')
    
    def play_sound(self, sound_name):
        """Play a sound effect."""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"[Sound] Error playing {sound_name}: {e}")
    
    def play_footstep(self):
        """Play the next footstep sound in sequence."""
        if self.footstep_sounds:
            try:
                self.footstep_sounds[self.footstep_index].play()
                self.footstep_index = (self.footstep_index + 1) % len(self.footstep_sounds)
            except Exception as e:
                print(f"[Sound] Error playing footstep: {e}")
    
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
            
            # Knight Attack3 second swing sound (frame 5 is when second swing starts)
            if (self.current_action == 'Attack3' and self.name == 'knight' and 
                self.frame_index == 5 and not self.attack3_second_swing_played):
                self.play_sound('attack3_second')
                self.attack3_second_swing_played = True
            
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
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= 1
        
        # Handle dodge movement
        if self.dodging:
            self.dodge_timer -= 1
            dodge_speed = (DODGE_DISTANCE / DODGE_DURATION) * scale
            dx = dodge_speed * self.dodge_direction
            
            if self.dodge_timer <= 0:
                self.dodging = False
            
            # Apply gravity during dodge
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
            
            self.x += dx
            self.y += dy
            return
        
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
                # Play footstep sounds during run animation
                # Play at specific run animation frames (alternating feet)
                run_frames = self.animation_config.get('Run', 8)
                footstep_frames = [1, run_frames // 2 + 1]  # Two footsteps per run cycle
                if self.frame_index in footstep_frames and self.frame_index != self.last_run_frame:
                    self.play_footstep()
                    self.last_run_frame = self.frame_index
            else:
                self.current_action = 'Idle'
                self.last_run_frame = -1  # Reset when not running
        
        # Apply gravity
        self.vel_y -= gravity
        dy = self.vel_y
        
        # Horizontal boundaries
        if self.x + dx < 0:
            dx = -self.x
        if self.x + self.RECT_WIDTH + dx > screen_width:
            dx = screen_width - self.x - self.RECT_WIDTH
        
        # Track if we were in the air before this frame
        was_in_air = self.jump
        
        # Ground collision
        if self.y + dy < ground_y:
            self.vel_y = 0
            self.jump_count = 0
            self.jump = False
            dy = ground_y - self.y
            
            # Play landing sound if we just landed (were in air, now on ground)
            if was_in_air:
                self.play_sound('land')
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
            self.play_sound('jump')
    
    def do_dodge(self):
        """Trigger dodge/dash in the direction the fighter is facing."""
        if not self.dodging and not self.attacking and self.dodge_cooldown == 0 and self.alive:
            self.dodging = True
            self.dodge_timer = DODGE_DURATION
            self.dodge_cooldown = DODGE_COOLDOWN
            # Dash in the direction we're facing (flip=True means facing left)
            self.dodge_direction = -1 if self.flip else 1
    
    def do_attack(self, attack_type):
        """Trigger attack."""
        if not self.attacking and self.attack_cooldown == 0 and self.alive:
            self.attacking = True
            self.attack_hits_registered = set()  # Reset for new attack
            self.attack_type = attack_type
            self.current_action = f'Attack{attack_type}'
            self.frame_index = 0
            self.animation_counter = 0
            self.attack3_second_swing_played = False
            
            # Play attack sound
            if attack_type == 3 and self.name == 'knight':
                # Knight Attack3 has two swings - play first sound now
                self.play_sound('attack3_first')
            else:
                self.play_sound(f'attack{attack_type}')
    
    def check_attack_hit(self, target):
        """Check if attack hits target - only deals damage at specific impact frames."""
        if not self.attacking or not self.alive:
            return
        
        # Define impact frames for each character and attack
        # These are the frames where the weapon visually connects
        IMPACT_FRAMES = {
            'fantasy_warrior': {
                'Attack1': [5],
                'Attack2': [3],
                'Attack3': [5],
            },
            'knight': {
                'Attack1': [2],
                'Attack2': [3],
                'Attack3': [2, 7],  # Two hits in this combo attack
            }
        }
        
        # Get impact frames for this character and attack
        char_impacts = IMPACT_FRAMES.get(self.name, {})
        attack_impacts = char_impacts.get(self.current_action, [])
        
        # Check if current frame is an impact frame we haven't hit yet
        if self.frame_index not in attack_impacts:
            return
        
        # Already registered this hit frame
        if self.frame_index in self.attack_hits_registered:
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
                self.attack_hits_registered.add(self.frame_index)  # Mark this frame as hit
    
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
        self.attack_hits_registered = set()
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
        self.dodging = False
        self.dodge_cooldown = 0
        self.dodge_timer = 0
        
        # Reset sound state
        self.footstep_index = 0
        self.last_run_frame = -1
        self.attack3_second_swing_played = False
        
        if 'Idle' in self.animations and self.animations['Idle']:
            self.current_texture = self.animations['Idle'][0]
