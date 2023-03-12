import gi
import parquet

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def on_name_combo_changed(combo):
  tree_iter = combo.get_active_iter()
  if tree_iter is not None:
    model = combo.get_model()
    row_id, name = model[tree_iter][:2]
    print("Selected: ID=%d, name=%s" % (row_id, name))
  else:
    entry = combo.get_child()
    print("Entered: %s" % entry.get_text())

item_groups_store = Gtk.ListStore(int, str)
item_groups_store.append([0, "SEMUA KUMPULAN"])
item_groups = parquet.get_item_groups();
for i, v in enumerate(item_groups):
  item_groups_store.append([i+1, v])
item_groups_combo = Gtk.ComboBox.new_with_model_and_entry(item_groups_store)
item_groups_combo.connect("changed", on_name_combo_changed)
item_groups_combo.set_entry_text_column(1)
item_groups_combo.set_active(0)

item_categories_store = Gtk.ListStore(int, str)
item_categories_store.append([0, "SEMUA KATEGORI"])
item_categories = parquet.get_item_categories();
for i, v in enumerate(item_categories):
  item_categories_store.append([i+1, v])
item_categories_combo = Gtk.ComboBox.new_with_model_and_entry(item_categories_store)
item_categories_combo.connect("changed", on_name_combo_changed)
item_categories_combo.set_entry_text_column(1)
item_categories_combo.set_active(0)

hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
hbox.pack_start(item_groups_combo, False, False, 0)
hbox.pack_start(item_categories_combo, False, False, 0)

win = Gtk.Window()
win.connect("destroy", Gtk.main_quit)
win.add(hbox)
win.show_all()
Gtk.main()
