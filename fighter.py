import pygame


SPRITE_CONFIG = {
    'fantasy_warrior': {
        'scale_width': 350,
        'scale_height': 550, 
        'visual_y_pull': 120, 
        'death_y_adj': 30, 
    },
    'knight': {
        'scale_width': 350,
        'scale_height': 420,
        'visual_y_pull': 0,
        'death_y_adj': 30,
    }
}
# ==========================================

class Fighter():

    RECT_WIDTH = 105 
    RECT_HEIGHT = 225
    
    def __init__(self, x, y, name='fantasy_warrior', is_player_2=False):
        self.name = name
        self.flip = is_player_2 
        self.is_player_2 = is_player_2
        
        # --- DYNAMIC VISUAL CONFIGURATION (Fetches settings from SPRITE_CONFIG) ---
        config = SPRITE_CONFIG.get(self.name, SPRITE_CONFIG['fantasy_warrior'])
        
        self.scale_width = config['scale_width']
        self.scale_height = config['scale_height']
        self.visual_y_pull = config['visual_y_pull']
        self.death_y_adjustment = config['death_y_adj']
        
        self.x_offset = (self.scale_width - self.RECT_WIDTH) // 2 
        
        self.rectangle = pygame.Rect((x, y, self.RECT_WIDTH, self.RECT_HEIGHT))
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
        # These are original sprite sheet dimensions
        self.sprite_width = 200 
        self.sprite_height = 240
        
        self.load_animations()
        
        self.image = self.animations['Idle'][0]
    
    def load_animations(self):
        """Load all sprite animations using the instance's specific scale_width and scale_height"""
        # Define frame counts based on character
        if self.name == 'fantasy_warrior':
            animation_files = {
                'Idle': 10,
                'Run': 8,
                'Jump': 3,
                'Attack1': 7,
                'Attack2': 7,
                'Attack3': 8,
                'Take hit': 3,
                'Death': 7
            }
        elif self.name == 'knight':
            animation_files = {
                'Idle': 10,
                'Run': 10,
                'Jump': 3,
                'Attack1': 4,
                'Attack2': 6,
                'Attack3': 10,
                'hit': 1,
                'Death': 10
            }
        else:
            animation_files = {
                'Idle': 10,
                'Run': 8,
                'Jump': 3,
                'Attack1': 7,
                'Attack2': 7,
                'Attack3': 8,
                'Take hit': 3,
                'Death': 11
            }
        
        for action, num_frames in animation_files.items():
            self.animations[action] = []
            
            # Build correct file path based on character
            if self.name == 'knight':
                file_path = f'assets/images/characters/knight/{action}.png'
                try:
                    sprite_sheet = pygame.image.load(file_path).convert_alpha()
                except pygame.error:
                    print(f"Warning: Could not load {file_path}")
                    continue
            else:
                file_path = f'assets/images/characters/fantasy_warrior/{action}.png'
                try:
                    sprite_sheet = pygame.image.load(file_path).convert_alpha()
                except pygame.error:
                    print(f"Warning: Could not load {file_path}")
                    continue
            
            frame_width = sprite_sheet.get_width() // num_frames
            frame_height = sprite_sheet.get_height()
            
            for frame_idx in range(num_frames):
                frame = sprite_sheet.subsurface((frame_idx * frame_width, 0, frame_width, frame_height))
                
                # Scale using the instance's specific properties
                scaled_frame = pygame.transform.scale(frame, (self.scale_width, self.scale_height))
                self.animations[action].append(scaled_frame)
    
    def update_animation(self):
        if self.current_action not in self.animations or len(self.animations[self.current_action]) == 0:
            return
        
        # 1. FIX for Flicker: If death is complete, lock the image and stop updating
        if self.current_action == 'Death' and self.death_animation_done:
            return 
        
        self.animation_counter += 1
        frames_per_frame = 5
        
        if self.animation_counter >= frames_per_frame:
            self.animation_counter = 0
            self.frame_index += 1
            
            max_frames = len(self.animations[self.current_action])
            
            if self.frame_index >= max_frames:
                # Don't loop death animation - stay on last frame
                if self.current_action == 'Death':
                    self.frame_index = max_frames - 1
                    self.death_animation_done = True # Set flag to stop further updates
                else:
                    self.frame_index = 0
                
                if self.current_action in ['Attack1', 'Attack2', 'Attack3']:
                    self.attacking = False
                    self.attack_cooldown = 20
            
        # Ensure frame_index is valid before accessing
        if self.current_action in self.animations and len(self.animations[self.current_action]) > 0:
            safe_index = min(self.frame_index, len(self.animations[self.current_action]) - 1)
            self.image = self.animations[self.current_action][safe_index]

    def move(self, dx, dy, screen_width, screen_height, surface, target):
        SPEED = 10
        GRAVITY = 2

        # Check if health depleted
        if self.health <= 0:
            self.health = 0
            self.alive = False
            if self.current_action != 'Death':
                self.current_action = 'Death'
                self.frame_index = 0
                self.animation_counter = 0
            # Apply gravity only when dead to keep on ground
            self.vel_y += GRAVITY
            dy = self.vel_y
            GROUND_Y = screen_height - 110
            if self.rectangle.bottom + dy > GROUND_Y:
                self.vel_y = 0
                dy = GROUND_Y - self.rectangle.bottom
            self.rectangle.y += dy
            return  # Stop processing movement when dead

        key = pygame.key.get_pressed()

        # Decrease cooldowns
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # --- Input/Movement Logic ---
        
        is_running = False
        
        # Determine control keys based on player
        if not self.is_player_2:
            left_key, right_key, attack1_key, attack2_key = pygame.K_a, pygame.K_d, pygame.K_j, pygame.K_k
        else:
            left_key, right_key, attack1_key, attack2_key = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_COMMA, pygame.K_PERIOD # Using comma and period for P2 attacks
            
        if not self.attacking:
            
            if key[left_key]:
                dx = -SPEED
                self.flip = True
                is_running = True
            if key[right_key]:
                dx = SPEED
                self.flip = False
                is_running = True
            
            # Attack logic - Check for J+K combo first
            if key[attack1_key] and key[attack2_key]:
                if self.attack_cooldown == 0:
                    self.attacking = True
                    self.attack_type = 3
                    self.current_action = 'Attack3'
                    self.frame_index = 0
                    self.animation_counter = 0
            elif key[attack1_key] or key[attack2_key]:
                if self.attack_cooldown == 0:
                    self.attacking = True
                    if key[attack1_key]:
                        self.attack_type = 1
                        self.current_action = 'Attack1'
                    else:
                        self.attack_type = 2
                        self.current_action = 'Attack2'
                    self.frame_index = 0
                    self.animation_counter = 0
            
            # Update action based on state
            elif self.vel_y < 0 or (self.vel_y > 0 and self.jump):
                # Only reset frame if action is changing to Jump
                if self.current_action != 'Jump':
                    self.frame_index = 0
                    self.animation_counter = 0
                self.current_action = 'Jump'
            elif is_running:
                self.current_action = 'Run'
            else:
                self.current_action = 'Idle'
        
        # Apply gravity
        self.vel_y += GRAVITY
        dy = self.vel_y

        # Make player stay on screen (horizontal)
        if self.rectangle.left + dx < 0:
            dx = -self.rectangle.left
        # Adjusted screen boundary calculation (the original was odd)
        if self.rectangle.right + dx > screen_width:
             dx = screen_width - self.rectangle.right
        
        # Make player stay on screen (ground)
        # Assuming the ground is at screen_height - 110
        GROUND_Y = screen_height - 110
        if self.rectangle.bottom + dy > GROUND_Y:
            self.vel_y = 0
            self.jump_count = 0 
            self.jump = False
            dy = GROUND_Y - self.rectangle.bottom
        else:
            self.jump = True
        
        self.rectangle.x += dx
        self.rectangle.y += dy 

    def attack(self, target):
        """Handle attack without drawing green box"""
        # Don't attack if dead
        if not self.alive:
            return
            
        self.attacking = True
        
        # Create invisible attack hitbox
        attack_range = 80
        if self.flip:
            attack_rect = pygame.Rect(self.rectangle.left - attack_range, self.rectangle.y, attack_range, self.rectangle.height)
        else:
            attack_rect = pygame.Rect(self.rectangle.right, self.rectangle.y, attack_range, self.rectangle.height)
        
        # Only deal damage if cooldown is 0
        if attack_rect.colliderect(target.rectangle) and target.hit_cooldown == 0:
            if self.attack_type == 1:
                damage = 15
            elif self.attack_type == 2:
                damage = 20
            else:  # Attack3
                damage = 35
            target.health -= damage
            target.hit_cooldown = 30
            # Optional: Add code to knock back the target

    def draw(self, surface, target):
        """Draw sprite with configurable scaling and positioning"""

        img = pygame.transform.flip(self.image, self.flip, False)

        # Draw X position: Hitbox X minus X_OFFSET (to center the sprite frame)
        draw_x = self.rectangle.x - self.x_offset
        
        # Draw Y position: Hitbox bottom minus sprite height, PLUS the visual pull
        # self.rectangle.bottom is the point aligned with the ground (GROUND_Y)
        draw_y = self.rectangle.bottom - self.scale_height + self.visual_y_pull

        # Death adjustment
        if self.current_action == 'Death':
            draw_y -= self.death_y_adjustment

        surface.blit(img, (draw_x, draw_y))

        self.update_animation()

        if self.attacking:
            self.attack(target)