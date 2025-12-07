"""
Health Bar Component
Draws and manages health bar display with responsive scaling
"""

from kivy.graphics import Rectangle, Color, Line
from kivy.core.window import Window


class HealthBar:
    """Health bar display for fighters with responsive scaling."""
    
    # Base dimensions (for 1000x600 screen)
    BASE_WIDTH = 300
    BASE_HEIGHT = 30
    BASE_OFFSET_Y = 50
    BASE_MARGIN = 20
    
    def __init__(self, is_flipped=False):
        self.is_flipped = is_flipped  # For enemy health bar (fills from right)
        self._update_dimensions()
    
    def _get_scale_factor(self):
        """Calculate scale factor based on screen size."""
        base_width = 1000
        base_height = 600
        width_scale = Window.width / base_width
        height_scale = Window.height / base_height
        return min(width_scale, height_scale)
    
    def _update_dimensions(self):
        """Update dimensions based on current screen size."""
        scale = self._get_scale_factor()
        
        self.width = int(self.BASE_WIDTH * scale)
        self.height = int(self.BASE_HEIGHT * scale)
        margin = int(self.BASE_MARGIN * scale)
        offset_y = int(self.BASE_OFFSET_Y * scale)
        
        self.y = Window.height - offset_y - self.height
        
        if self.is_flipped:
            self.x = Window.width - self.width - margin
        else:
            self.x = margin
    
    def draw(self, canvas, health):
        """Draw the health bar on the given canvas."""
        # Update dimensions in case window was resized
        self._update_dimensions()
        
        ratio = max(0, min(1, health / 100))
        
        with canvas:
            # Background (red)
            Color(1, 0, 0, 1)
            Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
            
            # Health (green)
            Color(0, 1, 0, 1)
            if self.is_flipped:
                # Fill from right for enemy
                health_width = self.width * ratio
                health_x = self.x + self.width - health_width
                Rectangle(pos=(health_x, self.y), size=(health_width, self.height))
            else:
                Rectangle(pos=(self.x, self.y), size=(self.width * ratio, self.height))
            
            # Border
            Color(1, 1, 1, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
