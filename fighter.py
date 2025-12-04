import pygame

class Fighter():
    def __init__(self, x, y):
        self.flip = False   
        self.rectangle = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.jump = False
        self.jump_count = 0
        self.max_jumps = 2 
        self.attack_type = 0
        self.attacking = False
        self.health = 100
        self.hit_cooldown = 0
        
        # Load sprite sheet and extract first frame
        sprite_sheet = pygame.image.load('assets/images/characters/fantasy_warrior/Idle.png').convert_alpha()
        # Idle has 10 frames, so divide width by 10 to get one frame
        frame_width = sprite_sheet.get_width() // 10
        frame_height = sprite_sheet.get_height()
        # Extract the first frame (x=0)
        self.image = sprite_sheet.subsurface((0, 0, frame_width, frame_height))
        # Scale it to match rectangle size
        self.image = pygame.transform.scale(self.image, (self.rectangle.width * 2, self.rectangle.height)) 
     
    def move(self, dx, dy, screen_width, screen_height, surface, target):
        SPEED = 10
        GRAVITY = 2

        key = pygame.key.get_pressed()

        # Decrease hit cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        if self.attacking == False:

        #movement

            if key[pygame.K_a]:
                dx = -SPEED
                self.flip = True
            if key[pygame.K_d]:
                dx = SPEED
                self.flip = False
        
        #attacks
            if key[pygame.K_j] or key[pygame.K_k]:
                self.attack(surface, target)
                if key[pygame.K_j]:
                    self.attack_type = 1
                if key[pygame.K_k]:
                    self.attack_type = 2
            else:
                self.attacking = False

            self.vel_y += GRAVITY
            dy = self.vel_y

        #make player face each other
        if target.rectangle.centerx > self.rectangle.centerx:
            self.flip = False
        else:
            self.flip = True

        # make player stay on screen (horizontal)
        if self.rectangle.left + dx < 0:
            dx = -self.rectangle.left
        if self.rectangle.right + dx > screen_width:
            dx = screen_width - self.rectangle.right
        
        # make player stay on screen (ground)
        if self.rectangle.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump_count = 0 
            dy = screen_height - 110 - self.rectangle.bottom
        
        self.rectangle.x += dx
        self.rectangle.y += dy 

    def attack(self, surface, target):    
        self.attacking = True
        attacking_rectangle = pygame.Rect(self.rectangle.centerx - (2 * self.rectangle.width * self.flip),  self.rectangle.y, 2 * self.rectangle.width, self.rectangle.height)
        pygame.draw.rect(surface, (0, 255, 0), attacking_rectangle)
        
        # Only deal damage if cooldown is 0 (prevents multiple hits)
        if attacking_rectangle.colliderect(target.rectangle) and target.hit_cooldown == 0:
            target.health -= 10
            target.hit_cooldown = 20  # 20 frames cooldown (~0.33 seconds at 60 FPS)

    def draw(self, surface, target):
        # Flip the sprite based on direction
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rectangle.x, self.rectangle.y))
        
        if self.attacking:
            self.attack(surface, target)        
      
       
        

    
