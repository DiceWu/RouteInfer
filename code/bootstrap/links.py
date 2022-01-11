import json
# Reading data back
graph = {}
with open('sanitized_rib.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(' ')
        aspath = parts[1:]
        for i in range(len(aspath)-1):
            as1 = aspath[i]
            as2 = aspath[i+1]
            if as1 not in graph:
                graph[as1] = []
            if as2 not in graph:
                graph[as2] = []
            if as2 not in graph[as1]:
                graph[as1].append(as2)
            if as1 not in graph[as2]:
                graph[as2].append(as1)

deg = {}

for asn in graph:
    deg[asn] = len(graph[asn])

sortdeg = sorted(deg.items(), key=lambda x: x[1], reverse=True)
with open('degree.txt','w') as f:
    for tup in sortdeg:
        f.write(str(tup[0])+' '+str(tup[1])+'\n')

with open('g.json','w') as f:
    json.dump(graph,f)
    
