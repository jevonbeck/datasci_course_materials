import re
import numpy as np
import pandas as pd
import utility as ut # local file


# format 311 calls into base structure
def get_calls_data():
    calls = pd.read_csv('./data/detroit-311.csv')
    calls_cols = calls.loc[:,['ticket_id', 'issue_type', 'lat', 'lng', 'address', 'ticket_created_date_time']]
    calls_cols['ticket_created_date_time'] = ut.get_easy_date(calls_cols['ticket_created_date_time'])
    calls_cols = calls_cols.rename(columns={'ticket_id' : 'incident_id', 'issue_type': 'sub_type', 'ticket_created_date_time': 'incident_date'})
    calls_cols.insert(1, 'incident_type', '311 call')
    return calls_cols


# format crime into base structure
def get_crime_data():
    crime = pd.read_csv('./data/detroit-crime.csv', low_memory=False) 
    crime_cols = crime[['INCINO', 'CATEGORY', 'LAT', 'LON', 'ADDRESS', 'INCIDENTDATE']]
    crime_cols = crime_cols[pd.notna(crime_cols['LAT'])]
    crime_cols = crime_cols[crime_cols.apply(lambda x: x['LAT'] != 0 and x['LAT'] <= 90 and x['LON'] != 0 and x['LON'] <= 90, axis=1)]
    crime_cols['INCIDENTDATE'] = ut.get_easy_date(crime_cols['INCIDENTDATE'])
    crime_cols = crime_cols.rename(columns={'INCINO' : 'incident_id', 'CATEGORY': 'sub_type', 'LAT': 'lat', 'LON': 'lng', 'INCIDENTDATE': 'incident_date', 'ADDRESS': 'address'})
    crime_cols.insert(1, 'incident_type', 'crime')
    return crime_cols


# format blight into base structure
def get_blight_data():
    blight = pd.read_csv('./data/detroit-blight-violations.csv', low_memory=False)
    blight_clean = blight[~blight['TicketIssuedDT'].str.match('^01/01/3')]
    blight_cols = blight_clean.loc[:,['TicketID', 'ViolationCode']]
    
    # extract co-ordinates from ViolationAddress and place in separate columns
    blight_coords = blight_clean['ViolationAddress'].str.split('\n').map(lambda x: x[len(x) - 1].replace('(', '').replace(')', '').replace(' ','').split(','))
    blight_cols['lat'] = pd.to_numeric(blight_coords.map(lambda x: x[0]))
    blight_cols['lng'] = pd.to_numeric(blight_coords.map(lambda x: x[1]))
    blight_cols['address'] = blight_clean['ViolationAddress'].str.replace('\n', ' ').str.replace(r'\(.*\)', '')
    
    blight_cols['incident_date'] = ut.get_easy_date(blight_clean['TicketIssuedDT'])
    
    blight_cols = blight_cols.rename(columns={'TicketID' : 'incident_id', 'ViolationCode': 'sub_type'})
    blight_cols.insert(1, 'incident_type', 'blight')
    return blight_cols


## get blight code mapping
def get_blight_mapping():
    blight = pd.read_csv('./data/detroit-blight-violations.csv', low_memory=False)
    blight_clean = blight[~blight['TicketIssuedDT'].str.match('^01/01/3')]
    return blight_clean.groupby(['ViolationCode', 'ViolDescription']).count().reset_index().loc[:, ['ViolationCode', 'ViolDescription']]
  

## format demolitions into base structure
def get_demolition_data():
    demolitions = pd.read_csv('./data/detroit-demolition-permits.tsv', sep='\t')
    demolitions_clean_date = demolitions[~demolitions['PERMIT_ISSUED'].str.match('01/01/112414')]
    
    def compute_co_ords(x):
        site = x['site_location']
        if site is np.nan or not re.search('\({1}-*[0-9].*\){1}', site):
            return np.nan
        else:
            if re.search('[A-Z]|[a-z]', site):        
                parts = site.split('\n')
                lat_lng = parts[len(parts) - 1]
            else:
                lat_lng = site
            
            return list(map(lambda x: float(x), lat_lng.replace('(', '').replace(')', '').replace(' ','').split(',')))
        
    def compute_subtype(x):    
        bld_des = x['DESCRIPTION']
        if bld_des is np.nan :
            return x['BLD_TYPE_USE']
        else:
            return bld_des
    
    demolitions_coords = demolitions_clean_date.apply(compute_co_ords, axis=1)
    demolitions_clean = demolitions_clean_date[pd.notna(demolitions_coords)]
    coords_clean = demolitions_coords[pd.notna(demolitions_coords)]
    
    demolitions_cols = demolitions_clean.loc[:,['PERMIT_NO']]
    demolitions_cols['sub_type'] = demolitions_clean.apply(compute_subtype, axis=1)
    demolitions_cols['lat'] = pd.to_numeric(coords_clean.map(lambda x: x[0]))
    demolitions_cols['lng'] = pd.to_numeric(coords_clean.map(lambda x: x[1]))
    demolitions_cols['address'] = demolitions_clean['site_location'].str.replace('\n', ' ').str.replace(r'\(.*\)', '')
    
    demolitions_cols['incident_date'] = ut.get_date(pd.to_datetime(demolitions_clean['PERMIT_ISSUED'], format='%m/%d/%y'))
    
    demolitions_cols = demolitions_cols.rename(columns={'PERMIT_NO' : 'incident_id'})
    
    unique_demolitions = demolitions_cols.groupby(['incident_id']).count().reset_index()
    valid_demolitions = unique_demolitions[unique_demolitions['address'] <= 1]['incident_id'].to_list()
    demolitions_cols = demolitions_cols[demolitions_cols['incident_id'].isin(valid_demolitions)]
    
    demolitions_cols.insert(1, 'incident_type', 'demolitions')
    return demolitions_cols

# produce final incident data with building and area ids
def create_incident_data():
    # Ensure that we only accept incidents with 1 address per building.
    # This accounts for close buildings and address inconsistencies (spelling, variations, etc)
    # and is a data sanity check for incidents that can take place multiple times at the same building.
    # Note that demolition incidents are verified differently
    datasets = [get_calls_data(), get_crime_data(), get_blight_data()]
    
    trusted_datasets = []
    for dataset in datasets:
        dataset['building_id'] = ut.create_building_id_series(dataset)
        addresses_per_building = dataset.groupby(['building_id','address']).count().reset_index().groupby(['building_id']).count().reset_index()
        trusted_buildings = addresses_per_building[addresses_per_building['address'] <= 1]['building_id'].to_list()
        trusted_building_incidents = dataset[dataset['building_id'].isin(trusted_buildings)]
        trusted_datasets.append(trusted_building_incidents)
    
    # Ensure that we only accept 1 demolition incident per building, since a building can only be demolished once!
    # With only one incident per building, there is no need to check that the building is associated with multiple addresses as above
    demolitions = get_demolition_data()
    demolitions['building_id'] = ut.create_building_id_series(demolitions)
    demolitions_per_building = demolitions.groupby(['building_id']).count().reset_index()
    trusted_demolition_buildings = demolitions_per_building[demolitions_per_building['incident_id'] == 1]['building_id'].to_list()
    trusted_demolitions = demolitions[demolitions['building_id'].isin(trusted_demolition_buildings)]
    trusted_datasets.append(trusted_demolitions)
    
    incidents = pd.concat(trusted_datasets, ignore_index=True)
    incidents['area_id'] = ut.create_area_id_series(incidents)
    
    return incidents
    