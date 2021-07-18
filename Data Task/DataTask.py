# IMPORT LIBRARIES

import json
from pandas import json_normalize
import pandas as pd


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

df2 = df.join(attributes, on='ID', how='left', rsuffix='_attribute')
# I remove 'entity_id' to remove innecessary duplicates
df2.drop(columns=['Attribute Values', 'Attribute Names','entity_id'], inplace=True)


# Unify car Type
target['carType'].unique()
df2['BodyTypeText'].unique()

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
    
df3['ConditionTypeText'].unique()
target['condition'].unique()
df2['ConditionTypeText'] = df2['ConditionTypeText'].replace({'Occasion':'Used', 
                                                             'Oldtimer':'Original Condition', 
                                                             'Vorführmodell':'Used with guarantee', 
                                                             'Neu':'New'})

df3 = df2.drop_duplicates()
df3.columns




# 2) Normalisation
# Please normalise at least 2 attributes, and describe which normalisations are required for the other attributes 
# including examples.


#3) Integration
# Data Integration is to transform the supplier data with a specific data schema into a new dataset with target data schema,
# such as to:
# - keep any attributes that you can map to the target schema
# - discard attributes not mapped to the target schema
# - keep the number of records as unchanged



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