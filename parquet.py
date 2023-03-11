import pandas as pd
from opendosm import get_item_parquet, get_premise_parquet, get_pricecatcher_parquet

lookup_item = pd.read_parquet(get_item_parquet())
lookup_premise = pd.read_parquet(get_premise_parquet())
pricecatcher = pd.read_parquet(get_pricecatcher_parquet(None))

def get_item_groups():
  item_group = lookup_item.groupby('item_group')
  return [name for name, _ in item_group.size().items()]

def get_item_categories():
  item_category = lookup_item.groupby('item_category')
  return [name for name, _ in item_category.size().items()]

# item_code, item, unit, item_group, item_category
def search_items(item_category = None, item_group = None):
  if (item_category != None and item_group != None):
    q = "item_category == '%s' and item_group == '%s'" %(item_category, item_group)
    return lookup_item.query(q)
  elif (item_category != None):
    q = "item_category == '%s'" %(item_category)
    return lookup_item.query(q)
  elif (item_group != None):
    q = "item_group == '%s'" %(item_group)
    return lookup_item.query(q)
  q = "item_code != '%s'" %(-1)
  return lookup_item.query(q)

def get_premise_location():
  location = dict()
  for _, premise in lookup_premise.iterrows():
    if (premise.loc['state'] != None and premise.loc['state'] not in location):
      location[premise.loc['state']] = dict()
    if (premise.loc['district'] != None and premise.loc['district'] not in location[premise.loc['state']]):
      location[premise.loc['state']][premise.loc['district']] = list()
    if (premise.loc['premise_type'] != None and premise.loc['district'] not in location[premise.loc['state']][premise.loc['district']]):
      location[premise.loc['state']][premise.loc['district']].append(premise.loc['premise_type'])
  return location

# premise_code, premise, address, premise_type, state
def search_premises(state = None, district = None, premise_type = None):
  if (state != None and district != None and premise_type != None):
    q = "state == '%s' and district == '%s' and premise_type == '%s'" %(state, district, premise_type)
    return lookup_premise.query(q)
  elif (state != None and district != None):
    q = "state == '%s' and district == '%s'" %(state, district)
    return lookup_premise.query(q)
  elif (state != None):
    q = "state == '%s'" %(state)
    return lookup_premise.query(q)
  q = "premise_code != '%s'" %(-1)
  return lookup_premise.query(q)

# date, premise_code, item_code, price
def search_pricecatcher(premise_codes = None, item_codes = None):
  if 'date' in pricecatcher.columns: pricecatcher['date'] = pd.to_datetime(pricecatcher['date'])
  if (premise_codes != None and item_codes != None):
    q = f'premise_code in {premise_codes} and item_code in {item_codes}'
    return pricecatcher.query(q)
  elif (premise_codes != None):
    q = f'premise_code in {premise_codes}'
    return pricecatcher.query(q)
  elif (item_codes != None):
    q = f'item_code in {item_codes}'
    return pricecatcher.query(q)
  return pricecatcher


if (__name__ == '__main__'):
  try:
    print("groups:", len(get_item_groups()))
    print("categories:", len(get_item_categories()))
    print("location:", len(get_premise_location()))
    print("search_items all:", len(search_items().axes[0]))
    print("search_items by category:", len(search_items(item_category='AYAM').axes[0]))
    print("search_items by group:", len(search_items(item_group='BARANGAN SEGAR').axes[0]))
    group_category = search_items(item_category='AYAM', item_group='BARANGAN SEGAR')
    print("search_items by category & group:", len(group_category.axes[0]))
    print("search_premises all:", len(search_premises().axes[0]))
    print("search_premises by state:", len(search_premises(state = 'Johor').axes[0]))
    print("search_premises by state & district:", len(search_premises(state = 'Johor', district = 'Batu Pahat').axes[0]))
    location = search_premises(state = 'Johor', district = 'Batu Pahat', premise_type = 'Hypermarket');
    print("search_premises by state & district & premise_type:", len(location.axes[0]))
    item_codes = tuple([item_code for _, item_code in group_category.get('item_code').items()])
    premises_codes = tuple([premise_code for _, premise_code in location.get('premise_code').items()])
    print(len(search_pricecatcher(premise_codes = premises_codes, item_codes = item_codes).axes[0]))
    print(len(search_pricecatcher(premise_codes = premises_codes).axes[0]))
    print(len(search_pricecatcher(item_codes = item_codes).axes[0]))
    print(len(search_pricecatcher().axes[0]))
  except Exception as e:
    print(e)
