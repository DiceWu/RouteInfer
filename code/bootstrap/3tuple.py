import json

graph = {}

ASReFile = open("infer_rel/asrel.txt","r")
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
ASReFile.close()
def isvalley(as1,as2,as3):
    if graph[as1][as2] == -1 or graph[as2][as3] == 1:
        return False
    return True
threetup = {}
with open('sanitized_rib.txt','r') as f:
    for line in tqdm(f):
        parts = line.strip().split(' ')
        aspath = parts[1:]
        if len(aspath) < 3:
            continue
        for i in range(len(aspath)-2):
            as1 = aspath[i]
            as2 = aspath[i+1]
            as3 = aspath[i+2]
            if isvalley(as1,as2,as3):
                if as2 not in threetup:
                    threetup[as2] = {}
                if int(as1) < int(as3):
                    if as1 not in threetup[as2]:
                        threetup[as2][as1] = set()
                    threetup[as2][as1].add(as3)
                else:
                    if as3 not in threetup[as2]:
                        threetup[as2][as3] = set()
                    threetup[as2][as3].add(as1)
for as1 in threetup:
    for as2 in threetup[as1]:
        threetup[as1][as2] = list(threetup[as1][as2])
with open('threetup.json','w') as f:
    json.dump(threetup,f)


