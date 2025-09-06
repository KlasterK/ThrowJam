import pygame
from .ui import Button, Container, HBoxLayout, Label, Ruleset, Selector, SizePolicy, Stylesheet, Subwindow

class RedSubwindow(Subwindow):
    pass

class RedButton(Button):
    pass

class MainWindow(Container):
    def __init__(self, app, screen):
        super().__init__(None, Stylesheet(
            Selector(
                class_name='RedSubwindow',
                ruleset=Ruleset(border_color='#ff0000', bg_color='#ff6666'),
            ),
            Selector(
                class_name='RedButton',
                ruleset=Ruleset(
                    bg_color='#ff0000'
                )  
            ),
            Selector(
                class_name='RedButton',
                pseudo='hover',
                ruleset=Ruleset(
                    bg_color='#ff6600',
                ),
            ),
            Selector(
                class_name='RedButton',
                pseudo='pressed',
                ruleset=Ruleset(bg_color="#ff3300"),
            ),
        ))
        self._app = app
        self._screen = self.capture_surface = screen

    def show_game_over(self):
        def close_cb(widget, old_pseudo):
            if widget.pseudo != 'hover' or old_pseudo != 'pressed':
                return
            wnd.parent = None
        
        wnd = RedSubwindow('Game Over!', self)
        wnd.set_central_widget(layout := HBoxLayout(wnd))
        wnd.set_rect(w=350, h=100, centerx=self._screen.width / 2, centery=self._screen.height / 2)
        
        Label('Delete System32?', parent=layout).size_policy = SizePolicy(0, 0, 'max', 'max')
        Button('Yes', parent=layout, cb=close_cb)
        Button('No',  parent=layout, cb=close_cb)
        