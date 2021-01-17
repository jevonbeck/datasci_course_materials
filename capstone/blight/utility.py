import pandas as pd

# Date Utilities
def _get_easy_datetime(date_like_series):
  return pd.to_datetime(date_like_series, infer_datetime_format=True)

def get_date(date_series):
  return date_series.dt.date
    
def get_easy_date(date_like_series):
  return get_date(_get_easy_datetime(date_like_series))

# Location Utilities

_id_precision = 3
def _truncate_str(val):
    return val[0:(len(val)-_id_precision)]

def _get_format_string(location_precision):
    return '{:.' + f"{location_precision + _id_precision}" + 'f}'

def _make_location_id(lat ,lng):
    # Location IDs are based on co-ordinate data. Co-ordinates are
    # truncated such that the ID identifies the top left-hand
    # corner of the square enclosing the area that the location ID
    # is meant to cover.
    return str(_truncate_str(lat) + ',' + _truncate_str(lng))

def _make_coordinate(location_id):
    return pd.Series(list(map(lambda x : float(x), location_id.split(','))), index=['lat','lng'])
  
def _create_location_id(x, fmt_str):
    lat = fmt_str.format(x['lat'])
    lng = fmt_str.format(x['lng'])
    return _make_location_id(lat ,lng)    

def _create_location_id_series(locations_df, location_precision):
    fmt_str = _get_format_string(location_precision)
    return locations_df.apply(_create_location_id, args=(fmt_str,), axis=1)

def _create_nearby_location_ids(location_id, fmt_str,  location_steps):
    coord = _make_coordinate(location_id)
    lats = (location_steps + coord['lat']).map(lambda x: fmt_str.format(x))
    lngs = (location_steps + coord['lng']).map(lambda x: fmt_str.format(x))    
    return [_make_location_id(lat, lng) for lat in lats for lng in lngs]

def _create_nearby_location_series(location_ids, fmt_str,  location_steps):
    return location_ids.apply(_create_nearby_location_ids, args=(fmt_str,  location_steps,))

def flatten_nearby_series(nearby): 
    l = nearby.to_list()
    return [item for sublist in l for item in sublist]
    
def _create_nearby_location_set(location_ids, fmt_str,  location_steps):    
    nearby = _create_nearby_location_series(location_ids, fmt_str,  location_steps)
    return set(flatten_nearby_series(nearby))



_building_precision = 5
_nearby_building_step = 2
_building_fmt_str = _get_format_string(_building_precision)
_building_location_step_range = pd.Series(list(range(-_nearby_building_step,_nearby_building_step+1)))
_building_location_steps = _building_location_step_range * 10 ** (-_building_precision)

def create_building_id_series(locations_df):
    return _create_location_id_series(locations_df, _building_precision)

def create_nearby_building_ids(building_id):
    return _create_nearby_location_ids(building_id, _building_fmt_str, _building_location_steps)  

def get_nearby_buildings(building_ids):
    return _create_nearby_location_set(building_ids, _building_precision, _nearby_building_step)

def create_nearby_buildings_series(building_ids):
    return _create_nearby_location_series(building_ids, _building_fmt_str, _building_location_steps)


_area_precision = _building_precision - 1
_nearby_area_step = 1
_area_fmt_str = _get_format_string(_area_precision)
_area_location_step_range = pd.Series(list(range(-_nearby_area_step,_nearby_area_step+1)))
_area_location_steps = _area_location_step_range * 10 ** (-_area_precision)

def create_area_id_series(locations_df):
    return _create_location_id_series(locations_df, _area_precision)

def create_nearby_area_ids(area_id):
    return _create_nearby_location_ids(area_id, _area_fmt_str,  _area_location_steps)    

def get_nearby_areas(area_ids):
    return _create_nearby_location_set(area_ids, _area_fmt_str, _area_location_steps)

def create_nearby_areas_series(area_ids):
    return _create_nearby_location_series(area_ids, _area_fmt_str, _area_location_steps)
