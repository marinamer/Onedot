# IMPORT LIBRARIES

import json
from pandas import json_normalize
import pandas as pd
import numpy as np
import xlsxwriter


# 1) Pre-processing
# OPEN JSON FILE AND NORMALISE
data = []
with open('supplier_car.json', encoding='utf-8') as f:
  for line in f:
      data.append(json.loads(line))

df = json_normalize(data)
df.columns

# OPEN TARGET DATA FILE
target = pd.read_excel('Target Data.xlsx')
target.columns



# Pivot Attribute Names into different columns. Drop original columns

attributes = df.pivot_table(values='Attribute Values', index=df.ID, columns='Attribute Names', aggfunc='first')

df = df.join(attributes, on='ID', how='left', rsuffix='_attribute')
# I remove 'entity_id' to remove innecessary duplicates
df.drop(columns=['Attribute Values', 'Attribute Names','entity_id'], inplace=True)
df = df.drop_duplicates()

# 2) Normalisation
# Please normalise at least 2 attributes, and describe which normalisations are required for the other attributes 
# including examples.
# Unify car Type
target['carType'].unique()
df['BodyTypeText'].unique()

df2 = df.copy()
df2['BodyTypeText'] = df2['BodyTypeText'].replace({'Cabriolet':'Convertible / Roadster', 
                                                   'SUV / Geländewagen':'SUV', 
                                                   'Kombi':'Station Wagon', 
                                                   'Limousine':'Saloon', 
                                                   'Coupé':'Coupé',
                                                   'Kompaktvan / Minivan':'Other', 
                                                   'Pick-up':'Other', 
                                                   'Kleinwagen':'Other', 
                                                   'Sattelschlepper':'Other',
                                                   'Wohnkabine':'Other'
                                                   })

# Unify color column
target['color'].unique()
df2['BodyColorText'].unique()

df2['BodyColorText'] = df2['BodyColorText'].replace({'silber mét.':'Silver', 
                                                     'schwarz': 'Black',
                                                     'schwarz mét.':'Black',
                                                     'bordeaux': 'Red',
                                                     'anthrazit mét.':'Gray',
                                                     'grün mét.':'Green',
                                                     'rot':'Red',
                                                     'weiss':'White',
                                                     'grau':'Gray',
                                                     'grün':'Green' ,
                                                     'violett mét.': 'Purple', 
                                                     'grau mét.': 'Gray', 
                                                     'bordeaux mét.': 'Other', 
                                                     'blau mét.': 'Blue',
                                                     'rot mét.':'Red', 
                                                     'silber':'Silver', 
                                                     'blau':'Blue', 
                                                     'anthrazit':'Grey', 
                                                     'orange':'Orange', 
                                                     'braun mét.':'Brown',
                                                     'gelb':'Yellow', 
                                                     'gold mét.':'Gold', 
                                                     'beige mét.':'Beige', 
                                                     'orange mét.':'Orange', 
                                                     'weiss mét.':'White',
                                                     'beige':'Beige', 
                                                     'gelb mét.':'Yellow', 
                                                     'braun':'Brown', 
                                                     'gold':'Gold'
                                                     })

# Unify Car Condition 
df2['ConditionTypeText'].unique()
target['condition'].unique()
df2['ConditionTypeText'] = df2['ConditionTypeText'].replace({'Occasion':'Used', 
                                                             'Oldtimer':'Original Condition', 
                                                             'Vorführmodell':'Used with guarantee', 
                                                             'Neu':'New'})





df2['ConsumptionTotalText'].loc[df2['ConsumptionTotalText'] != 'null'] = 'l_km_consumption'

df2['ConsumptionTotalText'].loc[df2['ConsumptionTotalText'] == 'null'] = np.nan

df2['ConsumptionTotalText'].unique()
target['fuel_consumption_unit'].unique()

#3) Integration
# Data Integration is to transform the supplier data with a specific data schema into a new dataset with target data schema,
# such as to:
# - keep any attributes that you can map to the target schema
# - discard attributes not mapped to the target schema
# - keep the number of records as unchanged

df3 = df2.copy()

df3.drop(columns=['ID', 'TypeName','TypeNameFull', 'Ccm', 'Co2EmissionText','ConsumptionRatingText', 'FuelTypeText',
       'Properties', 'Seats', 'Doors','TransmissionTypeText','DriveTypeText', 'Hp','InteriorColorText'],inplace=True)

df3.rename(columns={'MakeText':'make', 
                    'ModelText':'model',
                    'ModelTypeText':'model_variant', 
                    'BodyColorText':'color', 
                    'BodyTypeText':'carType',
                    'City':'city',
                    'ConditionTypeText':'condition',
                    'FirstRegMonth':'manufacture_month',
                    'FirstRegYear':'manufacture_year',
                    'Km':'mileage',
                    'ConsumptionTotalText':'fuel_consumption_unit'
                    }, inplace=True)


df3.columns

target.dtypes
df3.dtypes



df3['make'] = df3['make'].str.title()


# COUNTRY CODE
df3['country'] = np.nan
df3['country'] = df3['country'].astype(object)

cities = pd.read_csv('cities.csv')
citiescode = cities[['name','country_code']].copy()

citiescode.rename(columns={'name':'city', 'country_code':'country'}, inplace=True)
citiescode.dtypes

df3= df3.merge(citiescode, how='left', on='city')
df3.rename(columns={'country_y':'country'}, inplace=True)
df3.drop(columns=['country_x'], inplace=True)


# Currency column
df3['currency'] = np.nan

# drive column
df3['drive'] = np.nan

# milleage unit column
df3['mileage_unit'] = 'kilometer'

# price on request
df3['price_on_request'] = False

# type
df3['type'] = 'car'

# zip
df3['zip'] = np.nan

df3['city'].unique()

# Changing data types to match the target
df3 = df3.astype({'manufacture_year': 'int64', 'mileage': 'float64', 'manufacture_month':'float64', 'currency':'object', 
                  'drive':'object', 'zip':'object'})

df3 = df3.reindex(sorted(df3.columns), axis=1)

df3 = df3[['carType', 'color', 'condition', 'currency', 'drive',
           'city', 'country',  'make', 'manufacture_year',
           'mileage', 'mileage_unit', 'model',
           'model_variant', 'price_on_request', 'type', 'zip',
           'manufacture_month', 'fuel_consumption_unit']]


with pd.ExcelWriter('DataTask.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Pre-Processing', index=False)
    df2.to_excel(writer, sheet_name='Normalisation', index=False)
    df3.to_excel(writer, sheet_name='Integration', index=False)
    

# Deliverables
# - An Excel/LibreOffice spreadsheet (no csv, no txt) with 3 tabs showing the results of each step above (i.e., pre-processing/
# normalisation/integration)
# - A script (R/Python/SQL/etc.) that can be executed to provide the above Excel file
# - A customer presentation (PowerPoint or similar) to describe the above processing. Assume that the audience is the
# customer onboarding manager – someone with business knowledge, and medium technical knowledge. This presentation
# should include at least:
# o key facts of input / output, e.g., # attributes, # records
# o summary of changes you made to the input data
# o summary of changes you can potentially make to the input data, with examples
# o take-away message and actions to take for the customer