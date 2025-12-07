"""
Bot AI Component
Handles AI decision making for the enemy fighter
"""

import random
from config import ATTACK_RANGE, FIGHTER_SPEED


class BotAI:
    """AI controller for enemy fighter."""
    
    def __init__(self, fighter, difficulty='medium'):
        self.fighter = fighter
        self.difficulty = difficulty
        
        # AI timing
        self.decision_timer = 0
        self.decision_interval = self._get_decision_interval()
        
        # AI state
        self.current_action = 'idle'
        self.action_timer = 0
        
        # Difficulty settings
        self._setup_difficulty()
    
    def _setup_difficulty(self):
        """Set AI parameters based on difficulty."""
        if self.difficulty == 'easy':
            self.reaction_time = 30  # frames before reacting
            self.attack_chance = 0.3
            self.dodge_chance = 0.1
            self.aggression = 0.3
        elif self.difficulty == 'medium':
            self.reaction_time = 15
            self.attack_chance = 0.5
            self.dodge_chance = 0.3
            self.aggression = 0.5
        else:  # hard
            self.reaction_time = 5
            self.attack_chance = 0.7
            self.dodge_chance = 0.5
            self.aggression = 0.7
    
    def _get_decision_interval(self):
        """Get decision interval based on difficulty."""
        if self.difficulty == 'easy':
            return random.randint(20, 40)
        elif self.difficulty == 'medium':
            return random.randint(10, 25)
        else:
            return random.randint(5, 15)
    
    def update(self, target, screen_width):
        """Update AI decision making and control the fighter."""
        if not self.fighter.alive or not target.alive:
            self.fighter.move_left = False
            self.fighter.move_right = False
            return
        
        # Update decision timer
        self.decision_timer += 1
        
        if self.decision_timer >= self.decision_interval:
            self.decision_timer = 0
            self.decision_interval = self._get_decision_interval()
            self._make_decision(target, screen_width)
        
        # Update action timer
        if self.action_timer > 0:
            self.action_timer -= 1
        else:
            # Reset movement when action expires
            if self.current_action in ['move_left', 'move_right']:
                self.fighter.move_left = False
                self.fighter.move_right = False
                self.current_action = 'idle'
    
    def _make_decision(self, target, screen_width):
        """Make an AI decision based on game state."""
        # Calculate distance to target
        distance = abs(self.fighter.x - target.x)
        
        # Determine if we're facing the target
        facing_target = (
            (self.fighter.x < target.x and not self.fighter.flip) or
            (self.fighter.x > target.x and self.fighter.flip)
        )
        
        # If currently attacking, don't make new decisions
        if self.fighter.attacking:
            return
        
        # Close range - attack or dodge
        if distance < ATTACK_RANGE + 50:
            self._close_range_decision(target)
        # Medium range - approach or wait
        elif distance < ATTACK_RANGE + 200:
            self._medium_range_decision(target)
        # Far range - approach
        else:
            self._far_range_decision(target, screen_width)
    
    def _close_range_decision(self, target):
        """Decision making when close to target."""
        roll = random.random()
        
        # If target is attacking, maybe dodge
        if target.attacking and roll < self.dodge_chance:
            self._dodge(target)
            return
        
        # Attack chance
        if roll < self.attack_chance:
            self._do_attack()
        # Sometimes back off
        elif roll < self.attack_chance + 0.2:
            self._back_off(target)
        # Sometimes jump attack
        elif roll < self.attack_chance + 0.3:
            self.fighter.do_jump()
            self._do_attack()
    
    def _medium_range_decision(self, target):
        """Decision making at medium range."""
        roll = random.random()
        
        if roll < self.aggression:
            # Approach
            self._approach(target)
        elif roll < self.aggression + 0.2:
            # Jump approach
            self.fighter.do_jump()
            self._approach(target)
        else:
            # Wait/idle
            self.fighter.move_left = False
            self.fighter.move_right = False
            self.current_action = 'idle'
    
    def _far_range_decision(self, target, screen_width):
        """Decision making when far from target."""
        # Almost always approach when far
        if random.random() < 0.8:
            self._approach(target)
        else:
            # Occasionally jump while approaching
            self.fighter.do_jump()
            self._approach(target)
    
    def _approach(self, target):
        """Move towards the target."""
        if self.fighter.x < target.x:
            self.fighter.move_left = False
            self.fighter.move_right = True
            self.current_action = 'move_right'
        else:
            self.fighter.move_left = True
            self.fighter.move_right = False
            self.current_action = 'move_left'
        
        # Set action duration
        self.action_timer = random.randint(10, 30)
    
    def _back_off(self, target):
        """Move away from the target."""
        if self.fighter.x < target.x:
            self.fighter.move_left = True
            self.fighter.move_right = False
            self.current_action = 'move_left'
        else:
            self.fighter.move_left = False
            self.fighter.move_right = True
            self.current_action = 'move_right'
        
        self.action_timer = random.randint(5, 15)
    
    def _dodge(self, target):
        """Dodge away from target's attack."""
        self._back_off(target)
        # Maybe jump while dodging
        if random.random() < 0.4:
            self.fighter.do_jump()
    
    def _do_attack(self):
        """Perform an attack."""
        # Choose attack type
        attack_type = random.choice([1, 2])
        
        # Occasionally do special attack (both attacks)
        if random.random() < 0.15:
            attack_type = 3
        
        self.fighter.do_attack(attack_type)
        self.current_action = 'attacking'
