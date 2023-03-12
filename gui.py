import gi
import parquet

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class PriceCatcher(Gtk.Window):

  locations     = None
  group         = None
  category      = None
  state         = None
  district      = None
  premise_type  = None
  hbox          = None
  hboxcombobox  = None

  def __init__(self):
    super().__init__(title="OpendDOSM - PriceCatcher")

    self.set_border_width(10)

    item_groups_store = Gtk.ListStore(int, str)
    item_groups = ["SEMUA KUMPULAN", *parquet.get_item_groups()]
    for i, v in enumerate(item_groups):
      item_groups_store.append([i, v])
    item_groups_combo = Gtk.ComboBox.new_with_model_and_entry(item_groups_store)
    item_groups_combo.connect("changed", self.on_group_combo_changed)
    item_groups_combo.set_entry_text_column(1)
    item_groups_combo.set_active(0)

    item_categories_store = Gtk.ListStore(int, str)
    item_categories = ["SEMUA KATEGORI", *parquet.get_item_categories()]
    for i, v in enumerate(item_categories):
      item_categories_store.append([i, v])
    item_categories_combo = Gtk.ComboBox.new_with_model_and_entry(item_categories_store)
    item_categories_combo.connect("changed", self.on_category_combo_changed)
    item_categories_combo.set_entry_text_column(1)
    item_categories_combo.set_active(0)

    self.locations = parquet.get_premise_location()

    states_store = Gtk.ListStore(int, str)
    states = ["SEMUA NEGERI", *self.locations.keys()]
    for i, v in enumerate(states):
      states_store.append([i, v])
    states_combo = Gtk.ComboBox.new_with_model_and_entry(states_store)
    states_combo.connect("changed", self.on_state_combo_changed)
    states_combo.set_entry_text_column(1)
    states_combo.set_active(0)

    self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    self.hboxcombobox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    self.hboxcombobox.pack_start(item_groups_combo, False, False, 0)
    self.hboxcombobox.pack_start(item_categories_combo, False, False, 0)
    self.hboxcombobox.pack_start(states_combo, False, False, 0)

    self.hbox.pack_start(self.hboxcombobox, False, False, 0)

    button = Gtk.Button.new_with_label("Papar Data")
    button.connect("clicked", self.show_price_list)
    self.hbox.pack_start(button, False, False, 0)

    self.add(self.hbox)

  def hboxcombobox_append_district_combobox(self, state = None):
    if (state in self.locations):
      self.state = state
      self.district = None
      self.premise_type = None
      districts = ["SEMUA DAERAH", *self.locations[self.state].keys()]
      districts_store = Gtk.ListStore(int, str)
      for i, v in enumerate(districts):
        districts_store.append([i, v])
      districts_combo = Gtk.ComboBox.new_with_model_and_entry(districts_store)
      districts_combo.connect("changed", self.on_district_combo_changed)
      districts_combo.set_entry_text_column(1)
      districts_combo.set_active(0)
      self.hboxcombobox.pack_start(districts_combo, False, False, 0)
      districts_combo.show()
    else:
      self.state = None
      self.district = None
      self.premise_type = None

  def hboxcombobox_append_premise_type_combobox(self, district = None):
    if (district in self.locations[self.state]):
      self.district = district
      self.premise_type = None
      premises_types = ["SEMUA PREMIS", *self.locations[self.state][self.district]]
      premises_types_store = Gtk.ListStore(int, str)
      for i, v in enumerate(premises_types):
        premises_types_store.append([i, v])
      premises_types_combo = Gtk.ComboBox.new_with_model_and_entry(premises_types_store)
      premises_types_combo.connect("changed", self.on_premise_type_combo_changed)
      premises_types_combo.set_entry_text_column(1)
      premises_types_combo.set_active(0)
      self.hboxcombobox.pack_start(premises_types_combo, False, False, 0)
      premises_types_combo.show()
    else:
      self.district = None
      self.premise_type = None

  def show_price_list(self, button):
    # print(self.group, self.category, self.state, self.district, self.premise_type)
    item_codes = tuple([item_code for _, item_code in parquet.search_items(item_category=self.category, item_group=self.group).get('item_code').items()])
    premises_codes = tuple([premise_code for _, premise_code in parquet.search_premises(state=self.state, district=self.district, premise_type=self.premise_type).get('premise_code').items()])
    search_result = parquet.search_pricecatcher(premise_codes = premises_codes, item_codes = item_codes)
    price_list = parquet.group_price_list_by_premise_item(search_result)
    for premise in price_list:
      for item in price_list[premise]:
        for i in price_list[premise][item]:
          print(i)

  def on_group_combo_changed(self, combo):
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
      model = combo.get_model()
      row_id, name = model[tree_iter][:2]
      # print("Selected: ID=%d, name=%s" % (row_id, name))
      self.group = name if row_id != 0 else None
    else:
      self.group = None
      entry = combo.get_child()
      # print("Entered: %s" % entry.get_text())

  def on_category_combo_changed(self, combo):
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
      model = combo.get_model()
      row_id, name = model[tree_iter][:2]
      # print("Selected: ID=%d, name=%s" % (row_id, name))
      self.category = name if row_id != 0 else None
    else:
      self.category = None
      entry = combo.get_child()
      # print("Entered: %s" % entry.get_text())

  def on_state_combo_changed(self, combo):
    if (self.hboxcombobox != None):
      while (len(self.hboxcombobox.get_children()) > 3):
        self.hboxcombobox.remove(self.hboxcombobox.get_children()[len(self.hboxcombobox.get_children()) - 1])
      self.hboxcombobox.show()
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
      model = combo.get_model()
      row_id, name = model[tree_iter][:2]
      # print("State Selected: ID=%d, name=%s" % (row_id, name))
      self.hboxcombobox_append_district_combobox(name)
    else:
      entry = combo.get_child()
      # print("State Entered: %s" % entry.get_text())

  def on_district_combo_changed(self, combo):
    if (self.hboxcombobox != None):
      while (len(self.hboxcombobox.get_children()) > 4):
        self.hboxcombobox.remove(self.hboxcombobox.get_children()[len(self.hboxcombobox.get_children()) - 1])
      self.hboxcombobox.show()
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
      model = combo.get_model()
      row_id, name = model[tree_iter][:2]
      # print("District Selected: ID=%d, name=%s" % (row_id, name))
      self.hboxcombobox_append_premise_type_combobox(name)
    else:
      entry = combo.get_child()
      # print("District Entered: %s" % entry.get_text())

  def on_premise_type_combo_changed(self, combo):
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
      model = combo.get_model()
      row_id, name = model[tree_iter][:2]
      # print("Premise Type Selected: ID=%d, name=%s" % (row_id, name))
      self.premise_type = name if row_id != 0 else None
    else:
      self.premise_type = None
      entry = combo.get_child()
      # print("Premise Type Entered: %s" % entry.get_text())


win = PriceCatcher()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
