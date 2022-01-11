import json

with open('core.json','r') as f:
    graph = json.load(f)

outfile = open('corelink.txt','w')
for as1 in graph:
    for as2 in graph[as1]:
        if int(as1) < int(as2):
            outfile.write(as1+' '+as2+'\n')
outfile.close()
