"""
Control Layout Screen
Allows users to customize touch control positions, size, and opacity
"""

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Rectangle, Color, Line
from kivy.core.window import Window

from screens.base_screen import BaseScreen
from utils.settings import SettingsManager
from config import SCREENS, COLORS


class DraggableButton(Button):
    """A button that can be dragged to reposition and selected for editing."""
    
    def __init__(self, control_name, editor, **kwargs):
        super().__init__(**kwargs)
        self.control_name = control_name
        self.editor = editor
        self.dragging = False
        self.drag_offset = (0, 0)
        self.selected = False
        self._original_color = None
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Select this button
            self.editor.select_button(self.control_name)
            self.dragging = True
            self.drag_offset = (touch.x - self.x, touch.y - self.y)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.dragging:
            # Calculate new position
            new_x = touch.x - self.drag_offset[0]
            new_y = touch.y - self.drag_offset[1]
            
            # Keep within screen bounds
            new_x = max(0, min(Window.width - self.width, new_x))
            new_y = max(0, min(Window.height - self.height, new_y))
            
            self.pos = (new_x, new_y)
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            # Save position as percentage
            x_percent = self.x / Window.width
            y_percent = self.y / Window.height
            self.editor.update_control_position(self.control_name, x_percent, y_percent)
            return True
        return super().on_touch_up(touch)
    
    def set_selected(self, selected):
        """Set the selection state of the button."""
        self.selected = selected
        if selected:
            # Store original color and add highlight
            self._original_color = self.background_color[:]
            # Make it brighter/highlighted with a distinct border effect
            self.background_color = (1, 1, 0, 0.9)  # Yellow highlight
        else:
            # Restore original color
            if self._original_color:
                self.background_color = self._original_color


class ControlLayoutScreen(BaseScreen):
    """Control layout customization screen."""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.settings = SettingsManager.get_instance()
        self.control_buttons = {}
        self.selected_button = None  # Currently selected button name
        self.button_configs = {
            'left': {'text': '<', 'color': COLORS['p1_movement']},
            'right': {'text': '>', 'color': COLORS['p1_movement']},
            'atk1': {'text': 'A1', 'color': COLORS['p1_attack']},
            'atk2': {'text': 'A2', 'color': COLORS['p1_attack']},
            'jump': {'text': '^', 'color': COLORS['jump']},
            'dodge': {'text': 'DASH', 'color': (0.6, 0.3, 0.7, 1)},
        }
        self._create_ui()
    
    def _create_ui(self):
        """Create the control layout editor UI."""
        # Background
        with self.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg)
        
        # Instructions label
        self.instructions = Label(
            text='Tap a button to select it, then adjust size/opacity. Drag to reposition.',
            font_size=18,
            color=(1, 1, 1, 0.8),
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'top': 0.98}
        )
        self.add_widget(self.instructions)
        
        # Create control buttons
        self._create_control_buttons()
        
        # Create control panel at bottom
        self._create_control_panel()
    
    def _create_control_buttons(self):
        """Create draggable control buttons."""
        controls = self.settings.get_controls()
        
        for name, config in self.button_configs.items():
            pos_data = controls.get(name, {'x': 0.5, 'y': 0.5})
            x_pos = pos_data['x'] * Window.width
            y_pos = pos_data['y'] * Window.height
            
            # Get individual button scale and opacity
            btn_scale = self.settings.get_individual_button_scale(name)
            btn_opacity = self.settings.get_individual_button_opacity(name)
            base_size = int(80 * self._get_scale_factor() * btn_scale)
            btn_size = (base_size, base_size)
            
            btn = DraggableButton(
                control_name=name,
                editor=self,
                text=config['text'],
                size_hint=(None, None),
                size=btn_size,
                pos=(x_pos, y_pos),
                background_color=(*config['color'][:3], btn_opacity),
                font_size=int(24 * self._get_scale_factor() * btn_scale)
            )
            self.add_widget(btn)
            self.control_buttons[name] = btn
    
    def _create_control_panel(self):
        """Create the control panel with sliders and buttons."""
        panel_height = 180
        
        # Panel background
        self.panel = FloatLayout(
            size_hint=(1, None),
            height=panel_height,
            pos=(0, 0)
        )
        
        with self.panel.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)
            self.panel_bg = Rectangle(pos=(0, 0), size=(Window.width, panel_height))
        
        # Selected button label (shows which button is selected)
        self.selected_label = Label(
            text='No button selected - tap a button above',
            font_size=16,
            color=(1, 1, 0, 1),  # Yellow to match selection highlight
            size_hint=(None, None),
            size=(400, 30),
            pos=(20, panel_height - 25)
        )
        self.panel.add_widget(self.selected_label)
        
        # Size slider
        size_label = Label(
            text='Size:',
            font_size=16,
            size_hint=(None, None),
            size=(60, 30),
            pos=(20, panel_height - 60)
        )
        self.panel.add_widget(size_label)
        
        self.size_slider = Slider(
            min=0.5,
            max=1.5,
            value=1.0,
            size_hint=(None, None),
            size=(200, 30),
            pos=(80, panel_height - 60)
        )
        self.size_slider.bind(value=self._on_size_change)
        self.panel.add_widget(self.size_slider)
        
        self.size_value_label = Label(
            text='1.0x',
            font_size=14,
            size_hint=(None, None),
            size=(50, 30),
            pos=(290, panel_height - 60)
        )
        self.panel.add_widget(self.size_value_label)
        
        # Opacity slider
        opacity_label = Label(
            text='Opacity:',
            font_size=16,
            size_hint=(None, None),
            size=(70, 30),
            pos=(20, panel_height - 95)
        )
        self.panel.add_widget(opacity_label)
        
        self.opacity_slider = Slider(
            min=0.3,
            max=1.0,
            value=0.8,
            size_hint=(None, None),
            size=(200, 30),
            pos=(90, panel_height - 95)
        )
        self.opacity_slider.bind(value=self._on_opacity_change)
        self.panel.add_widget(self.opacity_slider)
        
        self.opacity_value_label = Label(
            text='80%',
            font_size=14,
            size_hint=(None, None),
            size=(50, 30),
            pos=(300, panel_height - 95)
        )
        self.panel.add_widget(self.opacity_value_label)
        
        # Buttons row
        btn_y = 20
        btn_height = 50
        btn_width = 120
        
        # Reset button
        reset_btn = Button(
            text='Reset',
            font_size=18,
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(20, btn_y),
            background_color=(0.7, 0.3, 0.3, 1)
        )
        reset_btn.bind(on_press=self._on_reset)
        self.panel.add_widget(reset_btn)
        
        # Save Preset button
        save_preset_btn = Button(
            text='Save Preset',
            font_size=18,
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(160, btn_y),
            background_color=(0.3, 0.6, 0.3, 1)
        )
        save_preset_btn.bind(on_press=self._on_save_preset)
        self.panel.add_widget(save_preset_btn)
        
        # Load Preset button
        load_preset_btn = Button(
            text='Load Preset',
            font_size=18,
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(300, btn_y),
            background_color=(0.3, 0.5, 0.7, 1)
        )
        load_preset_btn.bind(on_press=self._on_load_preset)
        self.panel.add_widget(load_preset_btn)
        
        # Back button (right side)
        back_btn = Button(
            text='Done',
            font_size=18,
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(Window.width - btn_width - 20, btn_y),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self._on_back)
        self.panel.add_widget(back_btn)
        
        self.add_widget(self.panel)
    
    def _get_scale_factor(self):
        """Calculate scale factor based on screen size."""
        base_width = 1000
        base_height = 600
        width_scale = Window.width / base_width
        height_scale = Window.height / base_height
        return min(width_scale, height_scale)
    
    def _update_bg(self, *args):
        """Update background size."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def update_control_position(self, control_name, x_percent, y_percent):
        """Update a control's position in settings."""
        self.settings.set_control_position(control_name, x_percent, y_percent)
    
    def select_button(self, control_name):
        """Select a button for individual editing."""
        # Deselect previous button
        if self.selected_button and self.selected_button in self.control_buttons:
            self.control_buttons[self.selected_button].set_selected(False)
            # Restore correct color for the deselected button
            config = self.button_configs.get(self.selected_button)
            if config:
                opacity = self.settings.get_individual_button_opacity(self.selected_button)
                self.control_buttons[self.selected_button].background_color = (*config['color'][:3], opacity)
        
        # Select new button
        self.selected_button = control_name
        if control_name in self.control_buttons:
            self.control_buttons[control_name].set_selected(True)
            
            # Update label with button name
            btn_names = {
                'left': 'LEFT',
                'right': 'RIGHT', 
                'atk1': 'ATTACK 1',
                'atk2': 'ATTACK 2',
                'jump': 'JUMP',
                'dodge': 'DASH'
            }
            self.selected_label.text = f'Selected: {btn_names.get(control_name, control_name.upper())}'
            
            # Update sliders to show this button's values
            btn_scale = self.settings.get_individual_button_scale(control_name)
            btn_opacity = self.settings.get_individual_button_opacity(control_name)
            self.size_slider.value = btn_scale
            self.opacity_slider.value = btn_opacity
            self.size_value_label.text = f'{btn_scale:.1f}x'
            self.opacity_value_label.text = f'{int(btn_opacity * 100)}%'
    
    def _on_size_change(self, slider, value):
        """Handle size slider change - applies to selected button."""
        self.size_value_label.text = f'{value:.1f}x'
        
        if self.selected_button:
            # Update individual button
            self.settings.set_individual_button_scale(self.selected_button, value)
            self._update_single_button_size(self.selected_button)
        else:
            # Update all buttons (backward compatibility)
            self.settings.set_button_scale(value)
            self._update_all_button_sizes()
    
    def _on_opacity_change(self, slider, value):
        """Handle opacity slider change - applies to selected button."""
        self.opacity_value_label.text = f'{int(value * 100)}%'
        
        if self.selected_button:
            # Update individual button
            self.settings.set_individual_button_opacity(self.selected_button, value)
            self._update_single_button_opacity(self.selected_button)
        else:
            # Update all buttons (backward compatibility)
            self.settings.set_button_opacity(value)
            self._update_all_button_opacity()
    
    def _update_single_button_size(self, control_name):
        """Update a single button's size."""
        if control_name in self.control_buttons:
            btn = self.control_buttons[control_name]
            scale = self.settings.get_individual_button_scale(control_name)
            base_size = int(80 * self._get_scale_factor() * scale)
            btn.size = (base_size, base_size)
            btn.font_size = int(24 * self._get_scale_factor() * scale)
    
    def _update_single_button_opacity(self, control_name):
        """Update a single button's opacity."""
        if control_name in self.control_buttons:
            btn = self.control_buttons[control_name]
            opacity = self.settings.get_individual_button_opacity(control_name)
            # Keep the yellow highlight if selected
            if btn.selected:
                btn.background_color = (1, 1, 0, 0.9)
                btn._original_color = (*self.button_configs[control_name]['color'][:3], opacity)
            else:
                config = self.button_configs.get(control_name)
                if config:
                    btn.background_color = (*config['color'][:3], opacity)
    
    def _update_all_button_sizes(self):
        """Update all button sizes based on global scale."""
        for name in self.control_buttons:
            self._update_single_button_size(name)
    
    def _update_all_button_opacity(self):
        """Update all button opacity."""
        for name in self.control_buttons:
            self._update_single_button_opacity(name)
    
    def _update_button_sizes(self):
        """Update all button sizes based on current scale."""
        self._update_all_button_sizes()

    def _update_button_opacity(self):
        """Update all button opacity."""
        self._update_all_button_opacity()
    
    def _on_reset(self, instance):
        """Reset to default layout."""
        self.settings.reset_to_default()
        # Deselect current button
        if self.selected_button and self.selected_button in self.control_buttons:
            self.control_buttons[self.selected_button].set_selected(False)
        self.selected_button = None
        self.selected_label.text = 'No button selected - tap a button above'
        self._refresh_buttons()
        self.size_slider.value = 1.0
        self.opacity_slider.value = 0.8
    
    def _on_save_preset(self, instance):
        """Show save preset dialog."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        name_input = TextInput(
            hint_text='Enter preset name',
            multiline=False,
            size_hint=(1, None),
            height=40
        )
        content.add_widget(name_input)
        
        buttons = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        
        cancel_btn = Button(text='Cancel', background_color=(0.5, 0.5, 0.5, 1))
        save_btn = Button(text='Save', background_color=(0.3, 0.6, 0.3, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(save_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title='Save Preset',
            content=content,
            size_hint=(0.6, 0.3),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=lambda x: self._save_preset(name_input.text, popup))
        
        popup.open()
    
    def _save_preset(self, name, popup):
        """Save the preset with given name."""
        if name.strip():
            self.settings.save_preset(name.strip())
            popup.dismiss()
    
    def _on_load_preset(self, instance):
        """Show load preset dialog."""
        presets = self.settings.get_presets()
        
        if not presets:
            # Show "no presets" message
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text='No saved presets'))
            ok_btn = Button(text='OK', size_hint=(1, None), height=50)
            content.add_widget(ok_btn)
            
            popup = Popup(
                title='Load Preset',
                content=content,
                size_hint=(0.5, 0.3)
            )
            ok_btn.bind(on_press=popup.dismiss)
            popup.open()
            return
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        for preset_name in presets:
            btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=5)
            
            load_btn = Button(
                text=preset_name,
                background_color=(0.3, 0.5, 0.7, 1)
            )
            delete_btn = Button(
                text='X',
                size_hint=(None, 1),
                width=50,
                background_color=(0.7, 0.3, 0.3, 1)
            )
            
            btn_layout.add_widget(load_btn)
            btn_layout.add_widget(delete_btn)
            content.add_widget(btn_layout)
            
            # Bind buttons (need to capture preset_name in closure)
            load_btn.bind(on_press=lambda x, n=preset_name: self._load_preset(n))
            delete_btn.bind(on_press=lambda x, n=preset_name: self._delete_preset(n))
        
        cancel_btn = Button(
            text='Cancel',
            size_hint=(1, None),
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        content.add_widget(cancel_btn)
        
        self.preset_popup = Popup(
            title='Load Preset',
            content=content,
            size_hint=(0.6, 0.5)
        )
        cancel_btn.bind(on_press=self.preset_popup.dismiss)
        self.preset_popup.open()
    
    def _load_preset(self, preset_name):
        """Load a preset."""
        self.settings.load_preset(preset_name)
        # Deselect current button
        if self.selected_button and self.selected_button in self.control_buttons:
            self.control_buttons[self.selected_button].set_selected(False)
        self.selected_button = None
        self.selected_label.text = 'No button selected - tap a button above'
        self._refresh_buttons()
        self.size_slider.value = 1.0
        self.opacity_slider.value = 0.8
        if hasattr(self, 'preset_popup'):
            self.preset_popup.dismiss()
    
    def _delete_preset(self, preset_name):
        """Delete a preset."""
        self.settings.delete_preset(preset_name)
        if hasattr(self, 'preset_popup'):
            self.preset_popup.dismiss()
        # Reopen the load dialog to show updated list
        self._on_load_preset(None)
    
    def _refresh_buttons(self):
        """Refresh all button positions from settings."""
        controls = self.settings.get_controls()
        
        for name, btn in self.control_buttons.items():
            pos_data = controls.get(name, {'x': 0.5, 'y': 0.5})
            btn.pos = (pos_data['x'] * Window.width, pos_data['y'] * Window.height)
            
            # Update individual button size and opacity
            scale = self.settings.get_individual_button_scale(name)
            opacity = self.settings.get_individual_button_opacity(name)
            base_size = int(80 * self._get_scale_factor() * scale)
            btn.size = (base_size, base_size)
            btn.font_size = int(24 * self._get_scale_factor() * scale)
            
            # Update color with opacity (unless selected)
            if not btn.selected:
                config = self.button_configs.get(name)
                if config:
                    btn.background_color = (*config['color'][:3], opacity)
    
    def _on_back(self, instance):
        """Save and go back."""
        self.settings.save()
        self.app.switch_screen(SCREENS['SETTINGS'])
    
    def on_enter(self):
        """Called when entering this screen."""
        # Reset selection state
        if self.selected_button and self.selected_button in self.control_buttons:
            self.control_buttons[self.selected_button].set_selected(False)
        self.selected_button = None
        self.selected_label.text = 'No button selected - tap a button above'
        self.size_slider.value = 1.0
        self.opacity_slider.value = 0.8
        self._refresh_buttons()
    
    def on_leave(self):
        """Called when leaving this screen."""
        # Deselect button when leaving
        if self.selected_button and self.selected_button in self.control_buttons:
            self.control_buttons[self.selected_button].set_selected(False)
            # Restore original color
            config = self.button_configs.get(self.selected_button)
            if config:
                opacity = self.settings.get_individual_button_opacity(self.selected_button)
                self.control_buttons[self.selected_button].background_color = (*config['color'][:3], opacity)
        self.selected_button = None
        self.settings.save()
