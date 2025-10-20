"""
Tray Logic To Remove Native OS Border While Maintaining Quit And Minimize Functionality

Class:
- SystemTray(root)
    Functions:
    - create_icon()
    - restore_window()
    - quit_app()
    - setup_tray()
    - minimize()
"""

import pystray
import threading
from PIL import Image, ImageDraw

class SystemTray:
    def __init__(self, root):
        self.root = root
        self.icon = None
        self.tray_thread = None

    def create_icon(self):
        # Icon W/H and Icon Background Colors
        sprite = Image.new("RGB", (64, 64), color=(46, 64, 90))
        d = ImageDraw.Draw(sprite)
        # Where Text Starts
        d.text((10, 20), "⌨️", fill=(255, 255, 255))
        return sprite

    def restore_window(self, icon=None, item=None):
        def restore():
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

        self.root.after(0, restore)
        # Remove Icon From Tray
        if self.icon:
            self.icon.stop()
            self.icon = None

    def quit_app(self, icon=None, item=None):
        # Remove Icon If Quit
        if self.icon:
            self.icon.stop()
        self.root.quit()

    def setup_tray(self):
        self.icon = pystray.Icon(
            "StenoApp",
            self.create_icon(),
            "Stenography Keyboard",
            menu=pystray.Menu(
                pystray.MenuItem("Restore", self.restore_window, default=True),
                pystray.MenuItem("Quit", self.quit_app)
            )
        )
        self.icon.run()

    def minimize(self):
        self.root.withdraw()
        if self.icon is None:
            self.tray_thread = threading.Thread(target=self.setup_tray, daemon=True)
            self.tray_thread.start()