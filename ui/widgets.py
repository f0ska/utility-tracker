from gi.repository import Gtk


def create_string_dropdown(items, selected=0):
    model = Gtk.StringList.new(items)
    factory = Gtk.SignalListItemFactory()

    def setup(factory, list_item):
        label = Gtk.Label()
        label.set_xalign(0)
        label.set_margin_start(8)
        label.set_margin_end(8)
        label.set_margin_top(6)
        label.set_margin_bottom(6)
        list_item.set_child(label)

    def bind(factory, list_item):
        item = list_item.get_item()
        label = list_item.get_child()
        label.set_text(item.get_string() if item else "")

    factory.connect("setup", setup)
    factory.connect("bind", bind)

    dropdown = Gtk.DropDown(model=model, factory=factory)
    dropdown.add_css_class("compact-dropdown")
    dropdown.set_selected(selected)
    return dropdown
