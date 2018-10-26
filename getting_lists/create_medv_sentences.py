f = open('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\getting_lists\\medical_venues_list.txt','r',encoding = 'utf-8').read()
lines = f.split('\n')

ndata = open('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\getting_lists\\MedVSentences List.txt','a',encoding = 'utf-8')
for i in range(0,len(lines)):
    ndata.write('Locate the nearest '+ lines[i])
    ndata.write('\n')
ndata.close()