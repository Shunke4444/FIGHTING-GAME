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
            self.reaction_time = 20  # frames before reacting
            self.attack_chance = 0.4
            self.dodge_chance = 0.2
            self.aggression = 0.4
        elif self.difficulty == 'medium':
            self.reaction_time = 10
            self.attack_chance = 0.6
            self.dodge_chance = 0.4
            self.aggression = 0.6
        elif self.difficulty == 'hard':
            # Faster reactions and higher aggression; less spammable dodging
            self.reaction_time = 3
            self.attack_chance = 0.85
            self.dodge_chance = 0.35
            self.aggression = 0.9
        else:  # nightmare
            # Very fast, highly aggressive, but don't dodge excessively — prefer punishes
            self.reaction_time = 1  # Nearly instant reactions
            self.attack_chance = 0.98
            self.dodge_chance = 0.25
            self.aggression = 0.995
    
    def _get_decision_interval(self):
        """Get decision interval based on difficulty."""
        if self.difficulty == 'easy':
            return random.randint(15, 30)
        elif self.difficulty == 'medium':
            return random.randint(8, 18)
        elif self.difficulty == 'hard':
            return random.randint(3, 10)
        else:  # nightmare
            return random.randint(1, 3)  # Near-instant decisions
    
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

        # If target is in attack recovery (can't immediately retaliate), prioritize punishing
        if getattr(target, 'attack_cooldown', 0) > 0:
            punish_chance = min(1.0, self.attack_chance + 0.25)
            if roll < punish_chance:
                # Prefer stronger or moving attacks when punishing
                if random.random() < 0.35:
                    # Special moving attack
                    self._do_attack(target)
                else:
                    self._do_attack(target)
                return

        # If target is actively attacking, prefer to capitalize on openings rather than spam dodges
        if target.attacking:
            # Less likely to dodge on harder difficulties; try to time a short back-off or small approach
            if roll < max(0.15, self.dodge_chance * 0.5):
                self._dodge(target)
                return
            # Slight chance to attempt a short punish after a tiny delay
            if roll < self.attack_chance:
                # Wait a couple frames to time a counter (give the engine a short pause)
                self.action_timer = random.randint(2, 6)
                self._do_attack(target)
                return

        # Default behavior: attack, back off, or jump-attack
        if roll < self.attack_chance:
            self._do_attack(target)
        elif roll < self.attack_chance + 0.2:
            self._back_off(target)
        elif roll < self.attack_chance + 0.3:
            self.fighter.do_jump()
            self._do_attack(target)
    
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
        # Use the dash dodge if available. Use configured dodge_chance so difficulty controls it.
        if self.fighter.dodge_cooldown == 0 and random.random() < self.dodge_chance:
            # Face away from target to dash away
            self.fighter.flip = self.fighter.x < target.x
            self.fighter.do_dodge()
        else:
            # Fall back to backing off; on higher difficulties this will be rarer
            self._back_off(target)
            # Maybe jump while dodging/backing
            if random.random() < 0.35:
                self.fighter.do_jump()
    
    def _do_attack(self, target=None):
        """Perform an attack."""
        # Choose attack type
        attack_type = random.choice([1, 2])
        
        # Occasionally do special attack (Attack 3 = A2 while moving)
        if random.random() < 0.15:
            attack_type = 3
            # Attack 3 requires movement, so start moving towards target
            if target is not None:
                if self.fighter.x < target.x:
                    self.fighter.move_left = False
                    self.fighter.move_right = True
                else:
                    self.fighter.move_left = True
                    self.fighter.move_right = False
            else:
                # Default: move in the direction we're facing
                if self.fighter.flip:
                    self.fighter.move_left = True
                    self.fighter.move_right = False
                else:
                    self.fighter.move_left = False
                    self.fighter.move_right = True
        
        self.fighter.do_attack(attack_type)
        self.current_action = 'attacking'
