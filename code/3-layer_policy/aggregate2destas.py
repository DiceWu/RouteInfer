import json
import copy
with open('../bootstrap/ip2as.json','r') as f:
    ip2as = json.load(f)

with open('prefix_policies.json','r') as f:
    bigdic = json.load(f)

desasdic = {}

conflict = []

for asn in bigdic:
    desasdic[asn] = {}
    if len(bigdic[asn]) == 0:
        continue
    temp = {}
    for prefix in bigdic[asn]:
        desas = ip2as[prefix][0]
        if desas not in temp:
            temp[desas] = {}
        for as1 in bigdic[asn][prefix]:
            if as1 not in temp[desas]:
                temp[desas][as1] = []
            for as2 in bigdic[asn][prefix][as1]:
                if as2 not in temp[desas][as1]:
                    temp[desas][as1].append(as2)
    desaslist = list(temp.keys())
    for desas in desaslist:
        if len(temp[desas]) <= 1:
            continue
        for as1 in temp[desas]:
            for as2 in temp[desas][as1]:
                if as2 in temp[desas] and as1 in temp[desas][as2]:
                    del temp[desas]
                    if asn not in conflict:
                        conflict.append(asn)
                    break
            else:
                continue
            break
    desasdic[asn] = copy.copy(temp)

with open('destas_policies.json','w') as f:
    json.dump(desasdic,f)

with open('conflictAS_destas.txt','w') as f:
    for asn in conflict:
        f.write(asn+'\n')



































        
    

