import json
import copy


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

def isvalley(as1,as2,as3):
    if graph[as1][as2] == -1 or graph[as2][as3] == 1:
        return False
    return True


with open('../bootstrap/threetup.json','r') as f:
    threetup = json.load(f)
qr = {}
with open('../bootstrap/quasi_router.txt','r') as f:
    for line in f:
        parts = line.strip().split(' ')
        qr[parts[0]] = int(parts[1])
for asn in ASN:
    if asn not in qr:
        qr[asn] = 1
policies = {}
def resetpolicy():
    for asn in qr:
        if qr[asn] == 1:
            policies[asn] = {}
        else:
            for i in range(qr[asn]):
                policies[asn+'_'+str(i)] = {}
resetpolicy()


with open('paths'+str(globalindex)+'.json','r') as f:
    paths = json.load(f)
    
with open('../3-layer_policy/prefix_policies.json','r') as f:
    policies = json.load(f)

link = {}
with open('../bootstrap/corelink.txt','r') as f:
    for line in f:
        as1,as2 = line.strip().split(' ')
        if as1 not in link:
            link[as1] = []
        if as2 not in link:
            link[as2] = []
        link[as1].append(as2)
        link[as2].append(as1)


def realnum(asn):
    if asn.find('_') > -1:
        return asn.split('_')[0]
    else:
        return asn

def announce(as1,as2,as3):
    if isvalley(as1,as2,as3) == True:
        if as2 not in threetup:
            return False
        if int(as1) < int(as3):
            if as1 not in threetup[as2] or as3 not in threetup[as2][as1]:
                return False
        else:
            if as3 not in threetup[as2] or as1 not in threetup[as2][as3]:
                return False
    return True

def routecmp(route1,route2,policy,desas):
    #local preference
    np1 = route1[0]
    np2 = route2[0]
    if desas in policy:
        if np1 in policy[desas] and np2 in policy[desas][np1]:
            return 1
        if np2 in policy[desas] and np1 in policy[desas][np2]:
            return -1
    if len(route1) < len(route2):
        return 1
    if len(route1) > len(route2):
        return -1
    if int(realnum(np1)) < int(realnum(np2)):
        return 1
    if int(realnum(np1)) > int(realnum(np2)):
        return -1
    if np1.find('_') > -1 and np2.find('_') > -1:
        if int(np1.split('_')[1]) < int(np2.split('_')[1]):
            return 1
        if int(np1.split('_')[1]) < int(np2.split('_')[1]):
            return -1
    return 0


def emulate(desas,tempqr,initroute,initqueue,initcache,deb=None):
    route = initroute
    queue = initqueue
    if len(queue) == 0:
        for nei in link[desas]:
            if nei == desas:
                continue
            if qr[desas] == 1:
                if qr[nei] == 1:
                    queue.append([nei,[desas]])
                else:
                    if nei in tempqr:
                        for i in range(tempqr[nei]):
                            queue.append([nei+'_'+str(i),[desas]])
                    else:
                        queue.append([nei+'_0',[desas]])
                        
            else:
                if qr[nei] == 1:
                    queue.append([nei,[desas+'_0']])
                else:
                    if nei in tempqr:
                        for i in range(tempqr[nei]):
                            queue.append([nei+'_'+str(i),[desas+'_0']])
                    else:
                        queue.append([nei+'_0',[desas+'_0']])
    cache = initcache
    ite = 0
    for diedai in range(5000000):   
        ite += 1  
        if len(queue) == 0:
            break
        item = queue.pop(0)
        
        asn = item[0]
        
        if asn in route:
            oldroute = copy.copy(route[asn])
        else:
            oldroute = []
            
        
        if item[1] != 'withdraw':
            annroute = item[1]
            if asn not in cache:
                cache[asn] = {}
            if len(cache[asn]) == 0:
                route[asn] = copy.copy(annroute)
                cache[asn][annroute[0]] = copy.copy(annroute)
            else:
                cache[asn][annroute[0]] = copy.copy(annroute)
                if annroute[0] == route[asn][0]:
                    if annroute == route[asn]:
                        continue
                    else:
                        bestroute = copy.copy(annroute)
                        keys = []
                        if desas in policies[asn]:
                            keys = list(policies[asn][desas].keys())
                        for neinp in cache[asn]:
                            if keys != [] and neinp in policies[asn][desas][keys[0]]:
                                continue
                            if routecmp(cache[asn][neinp], bestroute, policies[asn], desas) > 0:
                                bestroute = cache[asn][neinp]
                        route[asn] = copy.copy(bestroute)
                else:
                    if routecmp(route[asn], annroute, policies[asn], desas) < 0 :
                        if desas in policies[asn]:
                            keys = list(policies[asn][desas].keys())
                            if annroute[0] in policies[asn][desas][keys[0]]:
                                pass
                            else:
                                route[asn] = copy.copy(annroute)
                        else:
                            route[asn] = copy.copy(annroute)
                    
        else:
            wdnp = item[2]
            if wdnp in cache[asn]:
                del cache[asn][wdnp]
            if asn not in route:
                continue
            if wdnp == route[asn][0]:
                ks = []
                if desas in policies[asn]:
                    ks = list(policies[asn][desas].keys())
                if len(cache[asn]) > 0:
                    keys = list(cache[asn].keys())
                    bestroute = cache[asn][keys[0]]
                    for key in keys:
                        if ks != [] and key in policies[asn][desas][ks[0]]:
                            continue
                        if routecmp(cache[asn][key], bestroute, policies[asn], desas) > 0:
                            bestroute = cache[asn][key]
                    route[asn] = copy.copy(bestroute)
            if len(cache[asn]) == 0:
                oldnp = route[asn][0]
                del route[asn]
                for nei in link[realnum(asn)]:
                    as1 = nei
                    as2 = realnum(asn)
                    as3 = realnum(oldnp)
                    if announce(as1,as2,as3) == True:
                        if qr[as1] == 1:
                            queue.append([as1,'withdraw',asn])
                        else:
                            if as1 in tempqr:
                                for i in range(tempqr[as1]):
                                    queue.append([as1+'_'+str(i),'withdraw',asn])
                            else:
                                queue.append([as1+'_0','withdraw',asn])
                continue
                    
        

        newroute = route[asn]
        if oldroute == route[asn]:
            continue
        
        newpath = copy.copy(route[asn])
        newpath.insert(0,asn)
                
        for nei in link[realnum(asn)]:
            as1 = nei
            as2 = realnum(asn)
            as3 = realnum(newroute[0])
            if as1 == desas:
                continue
            
            if announce(as1,as2,as3) == False:
                if oldroute == []:
                    continue
                if announce(as1,as2,realnum(oldroute[0])) == True or realnum(as1) == realnum(as3):
                    if qr[as1] == 1:
                        queue.append([as1,'withdraw',asn])
                    else:
                        if as1 in tempqr:
                            for i in range(tempqr[as1]):
                                queue.append([as1+'_'+str(i),'withdraw',asn])
                        else:
                            queue.append([as1+'_0','withdraw',asn])
                continue
            if realnum(as1) == realnum(as3):
                continue
            if qr[as1] == 1:
                queue.append([as1,newpath])
            else:
                if as1 in tempqr:
                    for i in range(tempqr[as1]):
                        queue.append([as1+'_'+str(i),newpath])
                else:
                    queue.append([as1+'_0',newpath])
                    
    return route,cache
                        
def mycmp(x,y):
    return len(x[1]) - len(y[1])

def vali(pathset,route):
    for path in pathset:
        if path[1:] != route[path[0]]:
            print(path,route[path[0]])
            return False
    return True

desases = list(paths.keys())
globalcnt = 0

right = 0
wrong = 0
total = 0

def judge(route,asn,realpath):
    aslist = []
    if qr[asn] == 1:
        aslist.append(asn)
    elif asn not in tempqr or tempqr[asn] == 1:
        aslist.append(asn+'_0')
    elif tempqr[asn] > 1:
        for j in range(tempqr[asn]):
            aslist.append(asn+'_'+str(j))
    for asnn in aslist:
        if asnn in route:
            simpath = route[asnn]
            for j in range(len(simpath)):
                simpath[j] = realnum(simpath[j])
                if simpath == realpath:
                    return True
    return False



globalcnt = 0

for desas in desases:
    globalcnt += 1
    
    if globalcnt <= lastind:
        continue

    if desas in error:
        continue
    
    localtime = time.asctime(time.localtime(time.time()))
    print(globalcnt,desas,localtime)
    
    tempqr = tempqrdic[desas]
    
    initroute = {}
    initqueue = []
    initcache = {}
    
    route,cache = emulate(desas,tempqr,initroute,initqueue,initcache)
    tempdic = {}
    for path in paths[desas]:
        path = path.split(' ')
        if len(path) <= 2:
            continue
        as1 = path[0]
    
    for path in paths[desas]:
        path = path.split(' ')
        if len(path) <= 2:
            continue
        for i in range(len(path)-2):
            asn = path[i]

            realpath = path[i+1:]
            if qr[asn] == 1:
                tempasn = asn
            elif asn not in tempqr or tempqr[asn] == 1:
                tempasn = asn+'_0'
            else:
                for j in range(tempqr[asn]):
                    pp = route[asn+'_'+str(j)]
                    for k in range(len(pp)):
                        if realnum(pp[k]) != realpath[k]:
                            break
                    else:
                        break
                    continue
                else:
                    print('ERROR!')
                tempasn = asn+'_'+str(j)
            tempdic[tempasn] = [ [realpath[0],len(realpath)] ]
            for np in cache[tempasn]:
                if realnum(np) == realpath[0]:
                    continue
                tempdic[tempasn].append([np,len(cache[tempasn][np])])

with open('train.txt','w') as f:
    for asn in tempdic:
        f.write(str(asn)+' ')
        for item in tempdic[asn]:
            f.write(item[0]+','+str(item[1])+' ')
        f.write('\n')


                    
            
  





















