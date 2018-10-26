import pandas as pd
import pickle

symptom_disease_list = []

with open('../datasets/SymptomAndDiseasesList.pickle', 'rb') as f:
    symptom_disease_list = pickle.load(f)
    