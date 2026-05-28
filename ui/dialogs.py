from gi.repository import Gtk, Gdk


class ModalWindow(Gtk.Window):
    """Small Gtk.Window wrapper used instead of deprecated Gtk.Dialog."""

    def __init__(self, title, transient_for=None, modal=True):
        super().__init__(title=title, transient_for=transient_for, modal=modal)
        self.set_destroy_with_parent(True)

        self._content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self._content_area)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_controller)

    def get_content_area(self):
        return self._content_area

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False
