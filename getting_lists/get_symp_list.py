import numpy as np 
import pandas as pd

train_data = pd.read_csv('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\datasets\\Training.csv')
print(train_data.shape)
symps_list_r = []
for i in range(0,132):
    symps_list_r.append(train_data.columns[i])
# print(symps_list_r)
# lines = set(symps_list_r)
nd = open('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\getting_lists\\Symptom List.txt','w+',encoding = 'utf-8')
ndata = open('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\getting_lists\\Symptoms List.txt','w+',encoding = 'utf-8')
for i in range(0,132):
    ndata.write('"'+symps_list_r[i]+'","'+symps_list_r[i]+'"')
    ndata.write('\n')
    words = symps_list_r[i].split('_')
    symps_list_r[i] = ' '.join(words)
    nd.write(symps_list_r[i])
    nd.write('\n')
ndata.close()
nd.close()