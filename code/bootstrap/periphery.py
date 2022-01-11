import json

graph = {}
with open('g.json','r') as f:
    graph = json.load(f)

periphery = []

flag = True

while flag:
    flag = False
    for asn in graph:
        if len(graph[asn]) == 1:
            flag = True
            nei = graph[asn][0]
            graph[nei].remove(asn)
            del graph[asn]
            periphery.append(asn)
            break

with open('periphery.txt','w') as f:
    for asn in periphery:
        f.write(asn+'\n')

with open('core.json','w') as f:
    json.dump(graph,f)

    
