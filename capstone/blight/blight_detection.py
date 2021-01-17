import pandas as pd
import math

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

#from utility import create_nearby_area_ids # local file
from clean_data import create_incident_data # local file
#import matplotlib.pyplot as plt


incidents = create_incident_data()

# Week 2 Objective 1: obtain list of buildings
building_cnt_col = 'building_incident_cnt'
def incidents_to_buildings(incidents):
    return incidents.groupby(['area_id', 'building_id']).count()['incident_id'].reset_index().rename(columns={'incident_id': building_cnt_col})

all_buildings = incidents_to_buildings(incidents)

# Week 2 Objective 2: write functions to return 'incidents' associated with given 'building'
area_cnt_col = 'area_incident_cnt'
def incidents_to_areas(incidents):
    return incidents.groupby(['area_id']).count()['incident_id'].reset_index().rename(columns={'incident_id': area_cnt_col})

all_areas = incidents_to_areas(incidents)

#all_areas['nearby_area_incidents'] = all_areas['area_id'].transform(lambda area_id: incidents[incidents['area_id'].isin(create_nearby_area_ids(area_id))] )
#nearby_area_cnt_col = 'nearby_area_incident_cnt'
#all_areas[nearby_area_cnt_col] = all_areas['nearby_area_incidents'].transform(lambda x: x.shape[0])

all_buildings_extended = all_buildings.merge(all_areas, how='left', on='area_id')

building_data = all_buildings_extended.loc[:,['area_id', 'building_id', building_cnt_col, area_cnt_col]]
#building_data = all_buildings_extended.loc[:,['area_id', 'building_id', building_cnt_col, area_cnt_col, nearby_area_cnt_col]]

# sort_col = building_cnt_col
sort_col = area_cnt_col
# sort_col = nearby_area_cnt_col

# Week 3 Objective: construct training dataset
def get_twice_count_buildings(sorted_buildings, sort_col, count):
    return pd.concat([sorted_buildings.head(count), sorted_buildings.tail(count)], ignore_index=True) 

demolished_buildings = incidents_to_buildings(incidents[incidents['incident_type'] == 'demolitions'])
demolished_building_ids = demolished_buildings['building_id'].to_list()
is_demolished_building = building_data['building_id'].isin(demolished_building_ids)
    
building_data['extra_label'] = is_demolished_building.apply(lambda x: 'blighted' if x else 'not blighted')
    
def create_basic_training_data():
    # get useful demolished building data
    demolished_area_ids = demolished_buildings['area_id'].to_list()
    is_demolished_building_area = building_data['area_id'].isin(demolished_area_ids)
    
    demolished_buildings_with_cnt = building_data[is_demolished_building]
    useful_demolished = demolished_buildings_with_cnt[demolished_buildings_with_cnt[sort_col] > 1] # need at least 2 incidents per demolished building to have a chance at a good estimator (1 demolished and 1 other incident)    
    sorted_demolished = useful_demolished.sort_values(sort_col, ascending=False)
    
    # get useful non-demolished building data
    non_demolished_buildings = building_data[~is_demolished_building & is_demolished_building_area]    
    useful_non_demolished = non_demolished_buildings[non_demolished_buildings[sort_col] > 1] # at least 2 incidents needed per building to be on par with demolished buildings. No minimum required otherwise.
    sorted_non_demolished = useful_non_demolished.sort_values(sort_col, ascending=False)        
    
    # sample same size from each set
    set_size = min(sorted_demolished.shape[0], sorted_non_demolished.shape[0])
    quarter_count = math.floor(set_size / 4)
    
    demolished_sample = get_twice_count_buildings(sorted_demolished, sort_col, quarter_count)
    demolished_sample.insert(2, 'label', 'blighted')
       
    non_demolished_sample = get_twice_count_buildings(sorted_non_demolished, building_cnt_col, quarter_count)
    non_demolished_sample.insert(2, 'label', 'not blighted')
    
    return pd.concat([demolished_sample, non_demolished_sample], ignore_index=True)

basic_training_data = create_basic_training_data()

# Week 4 Objective: train and evaluate a simple model
def get_model_feature(interest_incidents, incident_cnt_col, location_id_col='building_id'):
    return interest_incidents.groupby([location_id_col]).count()['incident_id'].reset_index().rename(columns={'incident_id': incident_cnt_col})
    
def add_model_feature(model_data, model_feature, feature_col_name, location_id_col='building_id'):
    result = model_data.merge(model_feature, how='left', on=location_id_col)    
    result[feature_col_name] = result[feature_col_name].fillna(0)
    return result

blight_cnt_col = 'bldg_blight_incidents'
def create_simple_model_data(model_data):
    blight_incident_cnt = get_model_feature(incidents[incidents['incident_type'] == 'blight'], blight_cnt_col)
    return add_model_feature(model_data, blight_incident_cnt, blight_cnt_col)

simple_model_training_data = create_simple_model_data(basic_training_data)
simple_full_model_data = create_simple_model_data(building_data)

def evaluate_model(X, y, model, model_name):
    scores = cross_val_score(model, X, y, cv=5)
    print("Accuracy of %s model: %0.2f (+/- %0.2f)" % (model_name, scores.mean(), scores.std() * 2))

def predict_model(X, y, model):
    res = model.predict(X)
    acc_cnt = res == y
    correct = acc_cnt[acc_cnt == True].shape[0]
    print("Percentage correct = %0.2f" % (correct / acc_cnt.shape[0]))

def evaluate_and_predict_model(train_X, train_y, real_X, real_y, model_class, model_name):
    model = model_class.fit(train_X, train_y)
    evaluate_model(train_X, train_y, model, model_name)
    predict_model(real_X, real_y, model)

def evaluate_and_predict_model_by_cols(train, real, model_cols):
    train_X = train.loc[:,model_cols]
    train_y = train['label']
    real_X = real.loc[:,model_cols]
    real_y = real['extra_label']
    
    print(f'Evaluating columns {model_cols}' )    
    evaluate_and_predict_model(train_X, train_y, real_X, real_y, LogisticRegression(), 'Logistic Regression')
    evaluate_and_predict_model(train_X, train_y, real_X, real_y, SGDClassifier(), 'Stochastic Gradient Descent')
    evaluate_and_predict_model(train_X, train_y, real_X, real_y, SVC(), 'Support Vector Machine')
    evaluate_and_predict_model(train_X, train_y, real_X, real_y, KNeighborsClassifier(), 'K Nearest Neighbours (5 - default)')

evaluate_and_predict_model_by_cols(simple_model_training_data, simple_full_model_data, [blight_cnt_col])

# Week 5 Objective: Add more features [fix me below]

# Visualise training data (groupby => pivot => plot)

# Get timeline of 2 years before 1st demolition date
demolition_times = incidents[incidents['incident_type'] == 'demolitions'].sort_values('incident_date')
first_demo = demolition_times['incident_date'].values[0]
incidents_start_time = first_demo.replace(year=first_demo.year - 2)

#interest_incidents = incidents[
#  (incidents['area_id'].isin(simple_model_training_data['area_id'].unique())) &
#  (incidents['incident_date'] >= incidents_start_time)
#  ]
interest_incidents = incidents[
  (incidents['area_id'].isin(simple_model_training_data['area_id'].unique())) 
  ]

plot_data = interest_incidents.groupby(['area_id','incident_date','incident_type','sub_type']).count()['incident_id'].reset_index()
bldg_plot_data = interest_incidents.groupby(['building_id','incident_date','incident_type','sub_type']).count()['incident_id'].reset_index()

# Ideas
# 1) Find important incident types:
# - a) find demolition ones and non-demolition ones and see if there are similarities/differences 
# - b) find time-line importance of demolition ones
# 2) Look at timeline: 
# - a) Serious building demolition might have started around a certain time. Look initial 2 years back from demolition date.
# 3) Look at surrounding buildings/areas for incident and timeline insights as above.


# Find (non-demolition) incident sub-types that appear in demolition and/or non-demolition areas
def get_incident_types_by_demolition_location(incidents, location_id_col):
    # get the types of incidents that occur in each area
    locations_by_incident_type = incidents.groupby([location_id_col, 'incident_type', 'sub_type']).count()['incident_id'].reset_index()
    
    # split the types into those where demolitions occur and those where none occur
    is_demolition_location = locations_by_incident_type['incident_type'] == 'demolitions'
    demolition_location_types = locations_by_incident_type[is_demolition_location]
    non_demolition_location_types = locations_by_incident_type[~is_demolition_location]
    
    # Match each set of types by area. This identifies areas where both demolitions and non-demolition incidents take place.
    merged_location_types = non_demolition_location_types.merge(demolition_location_types, how='outer', on=location_id_col, suffixes=('_nd', '_d'))
    
    # Split the areas into those where demolitions occur and those where none occur, and identify the types in each area
    demolition_types = merged_location_types[merged_location_types['incident_type_d'] == 'demolitions'].loc[:, ['sub_type_nd', 'incident_type_d']].groupby(['sub_type_nd', 'incident_type_d']).count().reset_index()
    non_demolition_types = merged_location_types[merged_location_types['incident_type_d'].isna()].loc[:, ['sub_type_nd', 'incident_type_nd']].groupby(['sub_type_nd', 'incident_type_nd']).count().reset_index()
    
    # Match demolition/non-demolition area types by sub-type. This identifies which incident sub-types are solely demolition-related or non-demolition-related (or both)
    merged_types = demolition_types.merge(non_demolition_types, how='outer', on='sub_type_nd')
    return merged_types

interest_incident_types_by_demolition_bldg = get_incident_types_by_demolition_location(interest_incidents, 'building_id')

def create_complex_model_data(model_data):
    # Find incident types that ONLY occur in locations with demolition incidents
    demolition_only_types = interest_incident_types_by_demolition_bldg[interest_incident_types_by_demolition_bldg['incident_type_nd'].isna()]['sub_type_nd']
    
    # Find incident types that ONLY occur in locations with non-demolition incidents
    non_demolition_only_types = interest_incident_types_by_demolition_bldg[interest_incident_types_by_demolition_bldg['incident_type_d'].isna()]['sub_type_nd']
        
    demo_only_bldg_col = 'bldg_demolition_exclusive'
    demo_only_incidents = get_model_feature(incidents[incidents['sub_type'].isin(demolition_only_types)], demo_only_bldg_col)
    final_model_data = add_model_feature(model_data, demo_only_incidents, demo_only_bldg_col)
    
    non_demo_only_bldg_col = 'bldg_non_demolition_exclusive'    
    non_demo_only_incidents = get_model_feature(incidents[incidents['sub_type'].isin(non_demolition_only_types)], non_demo_only_bldg_col)
    final_model_data = add_model_feature(final_model_data, non_demo_only_incidents, non_demo_only_bldg_col)
    
    return final_model_data

full_model_training_data_bldg = create_complex_model_data(simple_model_training_data)
full_model_data_bldg = create_complex_model_data(simple_full_model_data)

model_cols = ['building_incident_cnt', 'area_incident_cnt', 'bldg_blight_incidents', 'bldg_demolition_exclusive', 'bldg_non_demolition_exclusive']
evaluate_and_predict_model_by_cols(full_model_training_data_bldg, full_model_data_bldg, model_cols)

