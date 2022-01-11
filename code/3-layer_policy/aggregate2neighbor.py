import json
import copy

conflict = []
with open('conflictAS_destas.txt','r') as f:
    for line in f:
        line = line.strip()
        conflict.append(line)

with open('destas_policies.json','r') as f:
    bigdic = json.load(f)

neidic = {}

conflict2 = []

for asn in bigdic:
    neidic[asn] = {}
    if len(bigdic[asn]) == 0:
        continue
    if asn in conflict:
        continue
    temp = {}
    for desas in bigdic[asn]:
        for as1 in bigdic[asn][desas]:
            if as1 not in temp:
                temp[as1] = []
            for as2 in bigdic[asn][desas][as1]:
                if as2 not in temp[as1]:
                    temp[as1].append(as2)
    if len(temp) > 1:
        for as1 in temp:
            for as2 in temp[as1]:
                if as2 in temp and as1 in temp[as2]:
                    temp = {}
                    if asn not in conflict2:
                        conflict2.append(asn)
                    break
            else:
                continue
            break
    neidic[asn] = copy.copy(temp)

with open('neighbor_policies.json','w') as f:
    json.dump(neidic,f)

with open('conflictAS_neighbor.txt','w') as f:
    for asn in conflict2:
        f.write(asn+'\n')

































        
    

