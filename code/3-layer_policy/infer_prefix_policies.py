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

with open('../bootstrap/ip2as.json','r') as f:
    ip2as = json.load(f)


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


with open('../bootstrap/paths.json','r') as f:
    paths = json.load(f)

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

#maxiter = 50

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

def routecmp(route1,route2,policy,prefix):
    #local preference
    np1 = route1[0]
    np2 = route2[0]
    if prefix in policy:
        if np1 in policy[prefix] and np2 in policy[prefix][np1]:
            return 1
        if np2 in policy[prefix] and np1 in policy[prefix][np2]:
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
def routecmp2(route1,route2):
    #local preference
    np1 = route1[0]
    np2 = route2[0]
    if len(route1) < len(route2):
        return 1
    if len(route1) > len(route2):
        return -1
    if int(np1) < int(np2):
        return 1
    if int(np1) > int(np2):
        return -1
    return 0
def shortestpath(desas,tempqr):
    route = {}
    queue = []
    for nei in link[desas]:
        queue.append([nei,[desas]])
        
    cache = {}
    ite = 0
    for diedai in range(10000000):
        ite += 1  
        
        if len(queue) == 0:
            break
        item = queue.pop(0)
        asn = item[0]
        #print(ite,asn)
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
                        bestroute = annroute
                        for neinp in cache[asn]:
                            if routecmp2(cache[asn][neinp], bestroute) > 0:
                                bestroute = cache[asn][neinp]
                        route[asn] = copy.copy(bestroute)
                else:
                    if routecmp2(route[asn], annroute) < 0 :
                        route[asn] = copy.copy(annroute)
                    
        else:
            wdnp = item[2]
            if wdnp in cache[asn]:
                del cache[asn][wdnp]
            if asn not in route:
                continue
            if wdnp == route[asn][0]:
                if len(cache[asn]) > 0:
                    keys = list(cache[asn].keys())
                    bestroute = cache[asn][keys[0]]
                    for key in keys:
                        if routecmp2(cache[asn][key], bestroute) > 0:
                            bestroute = cache[asn][key]
                    route[asn] = copy.copy(bestroute)
            if len(cache[asn]) == 0:
                oldnp = route[asn][0]
                del route[asn]
                for nei in link[asn]:
                    as1 = nei
                    as2 = asn
                    as3 = oldnp
                    if announce(as1,as2,as3) == True:
                        queue.append([as1,'withdraw',asn])
                continue

        newroute = route[asn]
        if oldroute == route[asn]:
            continue
        
        newpath = copy.copy(route[asn])
        newpath.insert(0,asn)
                
        for nei in link[asn]:
            as1 = nei
            as2 = asn
            as3 = newroute[0]
            if as1 == desas:
                continue
            if announce(as1,as2,as3) == False:
                if oldroute == []:
                    continue
                if announce(as1,as2,oldroute[0]) == True or as1 == as3:
                    queue.append([as1,'withdraw',asn])
                continue
            if as1 == as3:
                continue
            queue.append([as1,newpath])
                    
    return route,cache

def emulate(prefix,desas,tempqr,initroute,initqueue,initcache,deb=None):
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
    for diedai in range(10000000):
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
                        if prefix in policies[asn]:
                            keys = list(policies[asn][prefix].keys())
                        for neinp in cache[asn]:
                            if keys != [] and neinp in policies[asn][prefix][keys[0]]:
                                continue
                            if routecmp(cache[asn][neinp], bestroute, policies[asn], prefix) > 0:
                                bestroute = cache[asn][neinp]
                        route[asn] = copy.copy(bestroute)
                else:
                    if routecmp(route[asn], annroute, policies[asn], prefix) < 0 :
                        if prefix in policies[asn]:
                            keys = list(policies[asn][prefix].keys())
                            if annroute[0] in policies[asn][prefix][keys[0]]:
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
                if prefix in policies[asn]:
                    ks = list(policies[asn][prefix].keys())
                if len(cache[asn]) > 0:
                    keys = list(cache[asn].keys())
                    bestroute = cache[asn][keys[0]]
                    for key in keys:
                        if ks != [] and key in policies[asn][prefix][ks[0]]:
                            continue
                        if routecmp(cache[asn][key], bestroute, policies[asn], prefix) > 0:
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

prefixes = list(paths.keys())
globalcnt = 0
for prefix in prefixes:
    globalcnt += 1
    if len(ip2as[prefix]) > 1:
        continue
    else:
        desas = ip2as[prefix][0]
    count = {}
    preasnset = {}
    for path in paths[prefix]:
        for i in range(len(path)-1):
            asn = path[i]
            if qr[asn] > 1:
                if asn not in count:
                    count[asn] = []
                if path[i+1:] not in count[asn]:
                    count[asn].append(path[i+1:])
    tempqr = {}
    for asn in count:
        tempqr[asn] = len(count[asn])
    pathset = []
    for path in paths[prefix]:
        ann_path = []
        for i in range(len(path)):
            index = len(path) - i - 1
            asn = path[index]
            if qr[asn] == 1:
                ann_path.insert(0, asn)
            elif asn not in tempqr:
                ann_path.insert(0, asn+'_0')
            else:
                for j in range(tempqr[asn]):
                    if count[asn][j] == path[index+1:]:
                        break
                ann_path.insert(0, asn+'_'+str(j))
        pathset.append(ann_path)
    for path in pathset:
        for i in range(len(path)-2):
            asn = path[i+1]
            preasn = path[i]
            if asn not in preasnset:
                preasnset[asn] = []
            if preasn not in preasnset[asn]:
                preasnset[asn].append(preasn)
    nochange = False
    ite = 0
    route,cache = shortestpath(desas,tempqr)
    aslist1 = list(route.keys())
    aslist2 = list(cache.keys())
    aslist = set(aslist1) | set(aslist2)
    for asn in aslist:
        if asn in route:
            for i in range(len(route[asn])):
                if qr[route[asn][i]] > 1:
                    route[asn][i] = route[asn][i] + '_0'
        neilist = list(cache[asn].keys())
        for nei in neilist:
            for i in range(len(cache[asn][nei])):
                if qr[cache[asn][nei][i]] > 1:
                    cache[asn][nei][i] = cache[asn][nei][i] + '_0'
        for nei in neilist:
            if qr[nei] == 1:
                continue
            elif nei not in tempqr or tempqr[nei] == 1:
                cache[asn][nei+'_0'] = copy.copy(cache[asn][nei])
                del cache[asn][nei]
            elif tempqr[nei] > 1:
                for j in range(tempqr[nei]):
                    cache[asn][nei+'_'+str(j)] = copy.copy(cache[asn][nei])
                    cache[asn][nei+'_'+str(j)][0] = nei+'_'+str(j)
                del cache[asn][nei]
        if qr[asn] == 1:
            continue
        elif asn not in tempqr or tempqr[asn] == 1:
            if asn in route:
                route[asn+'_0'] = copy.copy(route[asn])
                del route[asn]
            cache[asn+'_0'] = copy.copy(cache[asn])
            del cache[asn]
        elif tempqr[asn] > 1:
            for j in range(tempqr[asn]):
                if asn in route:
                    route[asn+'_'+str(j)] = copy.copy(route[asn])
                cache[asn+'_'+str(j)] = copy.copy(cache[asn])
            if asn in route:
                del route[asn]
            del cache[asn]
    while True:
        ite += 1
        
        nochange = True
        wrongpath = []
        debugind = 0
        for i in range(len(pathset)-1,-1,-1):
            path = pathset[i]
            for j in range(len(path)-1):
                index = len(path)-2-j
                asn = path[index]
                realpath = path[index+1:]
                if route[asn] == realpath:
                    continue
                else:
                    nochange = False
                    
                    if len(wrongpath) == 0:
                        wrongpath = [asn,realpath]
                        debugind = i
                    else:
                        if len(realpath) < len(wrongpath[1]):
                            wrongpath = [asn,realpath]
                            debugind = i
                    break

        if nochange == True:
            break
        asn = wrongpath[0]
        realpath = wrongpath[1]
        simpath = route[asn]
        realpathlen = len(realpath)
        simnp = simpath[0]
        realnp = realpath[0]
        if simnp == realnp:
            print('error!')
            break
        if prefix not in policies[asn]:
            policies[asn][prefix] = {}
        if realnp not in policies[asn][prefix]:
            policies[asn][prefix][realnp] = []
        if simnp not in policies[asn][prefix][realnp]:
            policies[asn][prefix][realnp].append(simnp)
        
        for neinp in cache[asn]:
            if neinp == realnp:
                continue
            if asn in cache[asn][neinp]:
                continue
            if realnp in policies[asn][prefix] and neinp in policies[asn][prefix][realnp]:
                continue
            if len(cache[asn][neinp]) > realpathlen:
                continue
            if len(cache[asn][neinp]) == realpathlen and int(realnum(neinp)) > int(realnum(realnp)):
                continue
            if realnp not in policies[asn][prefix]:
                policies[asn][prefix][realnp] = []
            if neinp not in policies[asn][prefix][realnp]:
                policies[asn][prefix][realnp].append(neinp) 

        for nei in link[realnum(asn)]:
            neilist= []
            if qr[nei] == 1:
                neilist.append(nei)
            elif nei not in tempqr:
                neilist.append(nei+'_0')
            else:
                for j in range(tempqr[nei]):
                    neilist.append(nei+'_'+str(j))
            for neinp in neilist:
                if neinp not in route:
                    continue
                nn = route[neinp][0]
                if neinp == realnp:
                    continue
                if announce(realnum(asn),nei,realnum(nn)) == False:
                    continue
                if realnp in policies[asn][prefix] and neinp in policies[asn][prefix][realnp]:
                    continue    
                if (len(route[neinp]) + 1) > realpathlen:
                    continue
                if (len(route[neinp]) + 1) == realpathlen and int(realnum(neinp)) > int(realnum(realnp)):
                    continue
                if realnp not in policies[asn][prefix]:
                    policies[asn][prefix][realnp] = []
                if neinp not in policies[asn][prefix][realnp]:
                    policies[asn][prefix][realnp].append(neinp)
        
        if asn in preasnset:
            for preasn in preasnset[asn]:
                if realnp not in policies[asn][prefix]:
                    policies[asn][prefix][realnp] = []
                if preasn not in policies[asn][prefix][realnp]:
                    policies[asn][prefix][realnp].append(preasn)
            
        if realnum(realnp) == desas:
            newpath = []
        else:
            newpath = copy.copy(route[realnp])
        newpath.insert(0,realnp)
        initqueue = [[asn,newpath]]
        initroute = route
        initcache = cache
        route,cache = emulate(prefix,desas,tempqr,initroute,initqueue,initcache)
        if route == False:
            break
    del paths[prefix]


with open('prefix_policies.json','w') as f:
    json.dump(policies,f)
resetpolicy()


















































