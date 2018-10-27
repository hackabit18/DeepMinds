
f = open('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\getting_lists\\Symptom List.txt','r',encoding = 'utf-8').read()
lines = f.split('\n')

ndata = open('C:\\Users\\Rishabh\\Desktop\\HackABIT\\DeepMinds\\getting_lists\\Sentences List.txt','w+',encoding = 'utf-8')
for i in range(0, len(lines)):
    ndata.write('I am having '+ lines[i])
    ndata.write('\n')
ndata.close()