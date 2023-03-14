import gi
import parquet
import string

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class AlertDialog(Gtk.Dialog):
  def __init__(self, parent, title="", description=""):
    super().__init__(title=title, transient_for=parent, flags=0)
    self.add_buttons(
      Gtk.STOCK_OK, Gtk.ResponseType.OK
    )
    label = Gtk.Label(label=description)
    box = self.get_content_area()
    box.add(label)
    self.show_all()

class PriceCatcher(Gtk.Window):

  locations                 = None
  group                     = None
  category                  = None
  state                     = None
  district                  = None
  premise_type              = None
  items                     = None
  premises                  = None
  hbox_search_combobox      = None
  hbox_menu                 = None # wrap hbox_search_combobox and search_button
  vbox_premise_list         = None

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

    wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)  # wrap menu_grid and vbox_premise_list

    self.hbox_menu = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

    # all combobox
    self.hbox_search_combobox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    self.hbox_search_combobox.pack_start(item_groups_combo, False, False, 0)
    self.hbox_search_combobox.pack_start(item_categories_combo, False, False, 0)
    self.hbox_search_combobox.pack_start(states_combo, False, False, 0)
    self.hbox_menu.pack_start(self.hbox_search_combobox, False, False, 0)

    # search button
    search_button = Gtk.Button.new_with_label("Papar Data")
    search_button.connect("clicked", self.show_price_list)
    self.hbox_menu.pack_end(search_button, False, False, 0)  # wrap hbox_search_combobox and search_button

    menu_grid = Gtk.Grid()
    menu_grid.add(self.hbox_menu)

    wrapper.add(menu_grid)

    self.vbox_premise_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.NONE)
    label = Gtk.Label(label="NO DATA HERE", xalign=0)
    label.set_halign(Gtk.Align.CENTER)
    listbox.add(label)
    self.vbox_premise_list.add(listbox)

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.add(self.vbox_premise_list)

    wrapper.pack_start(scrolled_window, True, True, 0)

    self.add(wrapper)
    self.maximize()

  def hbox_search_combobox_append_district_combobox(self, state = None):
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
      self.hbox_search_combobox.pack_start(districts_combo, False, False, 0)
      districts_combo.show()
    else:
      self.state = None
      self.district = None
      self.premise_type = None

  def hbox_search_combobox_append_premise_type_combobox(self, district = None):
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
      self.hbox_search_combobox.pack_start(premises_types_combo, False, False, 0)
      premises_types_combo.show()
    else:
      self.district = None
      self.premise_type = None

  def show_price_list(self, button):
    if (self.group == None and self.category == None):
      dialog = AlertDialog(self, title="Peringatan!", description="Sila pilih kategori atau kumpulan barangan")
      response = dialog.run()
      # if response == Gtk.ResponseType.OK:
        # print("The OK button was clicked")
      # elif response == Gtk.ResponseType.CANCEL:
        # print("The Cancel button was clicked")
      dialog.destroy()
      return

    self.items = dict()
    item_codes = list()
    for item in parquet.search_items(item_category=self.category, item_group=self.group).itertuples():
      self.items[item[1]] = item
      item_codes.append(item[1])
    item_codes = tuple(item_codes)

    self.premises = dict()
    premises_codes = list()
    for premise in parquet.search_premises(state=self.state, district=self.district, premise_type=self.premise_type).itertuples():
      self.premises[premise[1]] = premise
      premises_codes.append(premise[1])
    premises_codes = tuple(premises_codes)

    search_result = parquet.search_pricecatcher(premise_codes = premises_codes, item_codes = item_codes)
    price_list = parquet.group_price_list_by_premise_item(search_result)
    self.vbox_premise_list_fill(price_list)

  def vbox_premise_list_fill(self, price_list):
    while (len(self.vbox_premise_list.get_children()) > 0):
      self.vbox_premise_list.remove(self.vbox_premise_list.get_children()[len(self.vbox_premise_list.get_children()) - 1])
    if len(price_list) == 0:
      listbox = Gtk.ListBox()
      listbox.show()
      listbox.set_selection_mode(Gtk.SelectionMode.NONE)
      label = Gtk.Label(label="NO DATA HERE", xalign=0)
      label.show()
      label.set_halign(Gtk.Align.CENTER)
      listbox.add(label)
      self.vbox_premise_list.add(listbox)
      return

    for premise in price_list:
      listbox = Gtk.ListBox()
      listbox.show()
      listbox.set_selection_mode(Gtk.SelectionMode.NONE)

      vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
      vbox.show()

      premise_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
      premise_box.show()

      label_premise = Gtk.Label(xalign=0)
      label_premise.set_markup(f'<span size="11999"><b>{str(self.premises[premise][2]).strip()}</b></span>')
      label_premise.show()
      premise_box.add(label_premise)

      label_address = Gtk.Label(xalign=0)
      label_address.set_markup(f'<span size="11999"><b>{" ".join(str(self.premises[premise][3]).split())}</b></span>')
      label_address.show()
      premise_box.add(label_address)

      label_state = Gtk.Label(label=str(self.premises[premise][5]).strip(), xalign=0)
      label_state.show()
      premise_box.pack_end(label_state, False, False, 0)

      label_district = Gtk.Label(label=str(self.premises[premise][6]).strip(), xalign=0)
      label_district.show()
      premise_box.pack_end(label_district, False, False, 0)

      label_premise_type = Gtk.Label(label=str(self.premises[premise][4]).strip(), xalign=0)
      label_premise_type.show()
      premise_box.pack_end(label_premise_type, False, False, 0)

      vbox.add(premise_box)

      listbox.add(vbox)
      for item in price_list[premise]:
        text_lines = list()
        for i in price_list[premise][item]:
          text_lines.append("\t" + str(i[1]).replace(" 00:00:00", "") + "\t\tRM" + str(format(float(i[4]), '.2f')))
        item_expander = Gtk.Expander(
          label=" ".join([str(self.items[item][2]), str(self.items[item][3]), str(self.items[item][4]), str(self.items[item][5])])
        )
        item_expander.show()
        item_expander.set_expanded(False)
        item_expander.show()

        details = Gtk.Label(label="\n".join(text_lines), xalign=0)
        details.set_halign(Gtk.Align.START)
        details.show()

        item_expander.add(details)
        vbox.add(item_expander)
      self.vbox_premise_list.add(listbox)


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
    if (self.hbox_search_combobox != None):
      while (len(self.hbox_search_combobox.get_children()) > 3):
        self.hbox_search_combobox.remove(self.hbox_search_combobox.get_children()[len(self.hbox_search_combobox.get_children()) - 1])
      self.hbox_search_combobox.show()
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
      model = combo.get_model()
      row_id, name = model[tree_iter][:2]
      # print("State Selected: ID=%d, name=%s" % (row_id, name))
      self.hbox_search_combobox_append_district_combobox(name)
    else:
      entry = combo.get_child()
      # print("State Entered: %s" % entry.get_text())

  def on_district_combo_changed(self, combo):
    if (self.hbox_search_combobox != None):
      while (len(self.hbox_search_combobox.get_children()) > 4):
        self.hbox_search_combobox.remove(self.hbox_search_combobox.get_children()[len(self.hbox_search_combobox.get_children()) - 1])
      self.hbox_search_combobox.show()
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
      model = combo.get_model()
      row_id, name = model[tree_iter][:2]
      # print("District Selected: ID=%d, name=%s" % (row_id, name))
      self.hbox_search_combobox_append_premise_type_combobox(name)
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
