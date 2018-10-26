import numpy as np 
import pandas as pd

train_data = np.array(pd.read_csv('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\datasets\\Training.csv'))

diseases_list_r = train_data[0:410,-1]

lines = set(diseases_list_r)
ndata = open('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\getting_lists\\Disease List.txt','w+',encoding = 'utf-8')
for line in lines:
    ndata.write('"'+line+'","'+line+'"')
    ndata.write('\n')
ndata.close()
