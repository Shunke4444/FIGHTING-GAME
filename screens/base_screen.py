"""
Base Screen Class
All screens inherit from this base class
"""

from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window


class BaseScreen(FloatLayout):
    """Base class for all game screens."""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.size_hint = (1, 1)
        
        # Bind to window size changes
        Window.bind(size=self.on_window_resize)
    
    def on_window_resize(self, window, size):
        """Handle window resize - override in subclasses if needed."""
        pass
    
    def on_enter(self):
        """Called when this screen becomes active."""
        pass
    
    def on_leave(self):
        """Called when leaving this screen."""
        pass
    
    def update(self, dt):
        """Update loop - override in subclasses if needed."""
        pass
