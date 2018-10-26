import pandas as pd
import pickle

symptom_list = []


data = pd.read_csv('DeepMinds\datasets\Training.csv')
disease_list = set(data['prognosis'])
disease_symptom_dictionary = {}
for i in disease_list:
    disease_symptom_dictionary[i] = set()

for index,row in data.iterrows():
    
    temp = row[row==1].index
    # print(row['prognosis'])
    for j in temp:
        disease_symptom_dictionary[row['prognosis']].add(j)

# for i in disease_list:
#     disease_symptom_dictionary[i]=set(disease_symptom_dictionary[i])
