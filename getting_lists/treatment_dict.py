data =  open ('getting_lists\\treatments.txt').read()
data = data.split('\n')
remedies = {}
for i,j in enumerate(data):
    data[i]=j.split('-')
    # remedies[data[i][0]]=data[i][1]
for row in data:
    remedies[row[0]]=row[1]
import pickle
with open('datasets/Treatment.pkl', 'wb') as f:
    pickle.dump(remedies, f, pickle.HIGHEST_PROTOCOL)