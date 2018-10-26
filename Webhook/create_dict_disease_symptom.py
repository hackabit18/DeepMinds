import pandas as pd
import pickle

symptom_list = []


data = pd.read_csv('DeepMinds\datasets\Training.csv')
disease_list = set(data['prognosis'])
disease_symptom_dictionary = {}

for index,row in data.iterrows():
    
    temp = row[row==1].index
    for j in temp:
        disease_symptom_dictionary[row['prognosis']].add(j)

