# IMPORT LIBRARIES
import json
from pandas import json_normalize
import pandas as pd
import numpy as np
import xlsxwriter


# 1) Pre-processing
# Open Json file and normalise
data = []
with open('supplier_car.json', encoding='utf-8') as f:
  for line in f:
      data.append(json.loads(line))

df = json_normalize(data)
df.columns

# Open Target data file
target = pd.read_excel('Target Data.xlsx')
target.columns

# Pivot Attribute Names and Attribute Values columns. Drop original columns
attributes = df.pivot_table(values='Attribute Values', index=df.ID, columns='Attribute Names', aggfunc='first')
df = df.join(attributes, on='ID', how='left', rsuffix='_attribute')

# Remove 'entity_id' to drop duplicates
df.drop(columns=['Attribute Values', 'Attribute Names','entity_id'], inplace=True)
df = df.drop_duplicates()


# 2) Normalisation
# Unify car Type
df2 = df.copy()
df2['BodyTypeText'] = df2['BodyTypeText'].replace({'Cabriolet':'Convertible / Roadster', 
                                                   'SUV / Geländewagen':'SUV', 
                                                   'Kombi':'Station Wagon', 
                                                   'Limousine':'Saloon',
                                                   'Kompaktvan / Minivan':'Other', 
                                                   'Pick-up':'Other', 
                                                   'Kleinwagen':'Other', 
                                                   'Sattelschlepper':'Other',
                                                   'Wohnkabine':'Other'
                                                   })

# Unify color column
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
# The unification of the color colummn could be automatised by direct translation (either through an external dataframe
# or through API to a service such as Google Translate).

# Unify Car Condition 
df2['ConditionTypeText'] = df2['ConditionTypeText'].replace({'Occasion':'Used', 
                                                             'Oldtimer':'Original Condition', 
                                                             'Vorführmodell':'Used with guarantee', 
                                                             'Neu':'New'})

# ConsumtionTotal normalised to match fuel_consumption_unit
df2['ConsumptionTotalText'].loc[df2['ConsumptionTotalText'] != 'null'] = 'l_km_consumption'
df2['ConsumptionTotalText'].loc[df2['ConsumptionTotalText'] == 'null'] = np.nan


#3) Integration
df3 = df2.copy()

# Dropping columns not present in target data structure
df3.drop(columns=['ID', 'TypeName','TypeNameFull', 'Ccm', 'Co2EmissionText','ConsumptionRatingText', 'FuelTypeText',
       'Properties', 'Seats', 'Doors','TransmissionTypeText','DriveTypeText', 'Hp','InteriorColorText'],inplace=True)

# Normalising column names
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


# Change 'make' column capitalisation to match target
df3['make'] = df3['make'].str.title()

# Country Code
df3['country'] = np.nan
df3['country'] = df3['country'].astype(object)

cities = pd.read_csv('cities.csv')
citiescode = cities[['name','country_code']].copy()

citiescode.rename(columns={'name':'city', 'country_code':'country'}, inplace=True)
citiescode.dtypes

df3= df3.merge(citiescode, how='left', on='city')
df3.rename(columns={'country_y':'country'}, inplace=True)
df3.drop(columns=['country_x'], inplace=True)

# Generating the missing columns
# Currency column
df3['currency'] = np.nan

# drive column
df3['drive'] = np.nan

# milleage unit column
df3['mileage_unit'] = 'kilometer'

# price on request column
df3['price_on_request'] = False

# type column
df3['type'] = 'car'
 
# zip column
df3['zip'] = np.nan

df3['city'].unique()

# Changing data types to match the target
df3 = df3.astype({'manufacture_year': 'int64', 'mileage': 'float64', 'manufacture_month':'float64', 'currency':'object', 
                  'drive':'object', 'zip':'object'})


# Reordering columns to match target for readability 
df3 = df3[['carType', 'color', 'condition', 'currency', 'drive',
           'city', 'country',  'make', 'manufacture_year',
           'mileage', 'mileage_unit', 'model',
           'model_variant', 'price_on_request', 'type', 'zip',
           'manufacture_month', 'fuel_consumption_unit']]


# Generate Excel file 
with pd.ExcelWriter('DataTask.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Pre-Processing', index=False)
    df2.to_excel(writer, sheet_name='Normalisation', index=False)
    df3.to_excel(writer, sheet_name='Integration', index=False)
    
