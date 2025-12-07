"""
Health Bar Component
Draws and manages health bar display
"""

from kivy.graphics import Rectangle, Color, Line


class HealthBar:
    """Health bar display for fighters."""
    
    def __init__(self, x, y, width=300, height=30, is_flipped=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_flipped = is_flipped  # For P2 health bar (fills from right)
    
    def draw(self, canvas, health):
        """Draw the health bar on the given canvas."""
        ratio = max(0, min(1, health / 100))
        
        with canvas:
            # Background (red)
            Color(1, 0, 0, 1)
            Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
            
            # Health (green)
            Color(0, 1, 0, 1)
            if self.is_flipped:
                # Fill from right for P2
                health_width = self.width * ratio
                health_x = self.x + self.width - health_width
                Rectangle(pos=(health_x, self.y), size=(health_width, self.height))
            else:
                Rectangle(pos=(self.x, self.y), size=(self.width * ratio, self.height))
            
            # Border
            Color(1, 1, 1, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
    
    def update_position(self, x, y):
        """Update the health bar position."""
        self.x = x
        self.y = y
