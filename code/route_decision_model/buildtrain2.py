import random
import json
colocated_ixp = {}
colocated_facility = {}
ixp_dict = {}
facility_dict = {}
with open('peeringdb.json','r') as f:
    data = json.load(f)
for i in data['netixlan']['data']:
    AS, ixp = i['asn'], i['ixlan_id']
    if ixp not in ixp_dict:
        ixp_dict[ixp] = [AS]
    else:
        ixp_dict[ixp].append(AS)
for i in data['netfac']['data']:
    AS, facility = i['local_asn'], i['fac_id']
    if facility not in facility_dict:
        facility_dict[facility] = [AS]
    else:
        facility_dict[facility].append(AS)    
for k, v in ixp_dict.items():
    as_pairs = [(str(p1), str(p2)) for p1 in v for p2 in v if p1 != p2]
    for pair in as_pairs:
        if (pair[0], pair[1]) not in colocated_ixp:
            colocated_ixp[(pair[0], pair[1])] = 0
        colocated_ixp[(pair[0], pair[1])] += 1
for k, v in facility_dict.items():
    as_pairs = [(str(p1), str(p2)) for p1 in v for p2 in v if p1 != p2]
    for pair in as_pairs:
        if (pair[0], pair[1]) not in colocated_facility:
            colocated_facility[(pair[0], pair[1])] = 0
        colocated_facility[(pair[0], pair[1])] += 1
graph = {}
ASN = set()
ASReFile = open("../bootstrap/infer_rel/asrel.txt","r")
for i in ASReFile:
    if i.find("#") > -1:
        continue
    i = i.strip()
    info = i.split('|')
    as1 = info[0]
    as2 = info[1]
    re = int(info[2])
    #AS1 is provider,AS2 is customer
    if re == -1:
        if as1 not in graph:
            graph[as1] = {}
        graph[as1][as2] = 1
        if as2 not in graph:
            graph[as2] = {}
        graph[as2][as1] = -1
    #AS1 is peer,AS2 is peer
    elif re == 0:
        if as1 not in graph:
            graph[as1] = {}
        graph[as1][as2] = 0
        if as2 not in graph:
            graph[as2] = {}
        graph[as2][as1] = 0
    ASN.add(as1)
    ASN.add(as2)
ASReFile.close()
with open('asinfo.json','r') as f:
    asinfo = json.load(f)
def realnum(asn):
    if asn.find('_') > -1:
        return asn.split('_')[0]
    else:
        return asn
lines = []
with open('train.txt','r') as f:
    lines += f.readlines()
        
random.shuffle(lines)

allnum = len(lines)

ind = int(allnum*0.9)

def r2vec(as1,asn,plen):
    vec = [0 for i in range(13)]
    asn = realnum(asn)
    plen = int(plen)
    
    rel = graph[as1][asn]
    vec[rel+1] = 1
    vec[3] = plen
    vec[4] = asinfo[asn]['degree']
    vec[5] = asinfo[asn]['asrank']
    if asinfo[asn]['type'] == 'Transit/Access':
        vec[6] = 1
    elif asinfo[asn]['type'] == 'Content':
        vec[7] = 1
    elif asinfo[asn]['type'] == 'Enterprise':
        vec[8] = 1
    elif asinfo[asn]['type'] == 'Education/Research':
        vec[9] = 1
    elif asinfo[asn]['type'] == 'Economy':
        vec[10] = 1
    if (as1,asn) not in colocated_ixp:
        vec[11] = 0
    else:
        vec[11] = colocated_ixp[(as1,asn)]
    if (as1,asn) not in colocated_facility:
        vec[12] = 0
    else:
        vec[12] = colocated_facility[(as1,asn)]
    return vec
    
globalind = 1
with open('train.txt','w') as f:
    for i in range(ind1):
        line = lines[i].strip()
        parts = line.split(' ')
        tempdic = {}
        for j in range(2,len(parts)):
            asn,plen = parts[j].split(',')
            realasn = realnum(asn)
            plen = int(plen)
            if realasn not in tempdic:
                tempdic[realasn] = plen
            else:
                tempdic[realasn] = min(tempdic[realasn],plen)
        asn,plen = parts[1].split(',')
        as1 = realnum(parts[0])
        vec = r2vec(as1,asn,plen)
        if None in vec:
            continue
        f.write('1 '+'qid:'+str(globalind))
        for i in range(13):
            f.write(' '+str(i+1)+':'+str(vec[i]))
        f.write('\n')
        for asn in tempdic:
            plen = tempdic[asn]
            vec = r2vec(as1,asn,plen)
            if None in vec:
                continue
            f.write('0 '+'qid:'+str(globalind))
            for i in range(13):
                f.write(' '+str(i+1)+':'+str(vec[i]))
            f.write('\n')
        globalind += 1

with open('test.txt','w') as f:
    for i in range(ind2,len(lines)):
        line = lines[i].strip()
        parts = line.split(' ')
        tempdic = {}
        for j in range(2,len(parts)):
            asn,plen = parts[j].split(',')
            realasn = realnum(asn)
            plen = int(plen)
            if realasn not in tempdic:
                tempdic[realasn] = plen
            else:
                tempdic[realasn] = min(tempdic[realasn],plen)
        asn,plen = parts[1].split(',')
        as1 = realnum(parts[0])
        vec = r2vec(as1,asn,plen)
        if None in vec:
            continue
        f.write('1 '+'qid:'+str(globalind))
        for i in range(13):
            f.write(' '+str(i+1)+':'+str(vec[i]))
        f.write('\n')
        for asn in tempdic:
            plen = tempdic[asn]
            vec = r2vec(as1,asn,plen)
            if None in vec:
                continue
            f.write('0 '+'qid:'+str(globalind))
            for i in range(13):
                f.write(' '+str(i+1)+':'+str(vec[i]))
            f.write('\n')        
        globalind += 1




















        
        
