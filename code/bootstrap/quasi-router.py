import json
# Reading data back

dic = {}

with open('sanitized_rib.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(' ')
        if len(parts) <= 2:
            continue
        aspath = parts[1:]
        prefix = parts[0]
        for i in range(len(aspath)-1):
            asn = aspath[i]
            path = aspath[i+1:]
            if asn not in dic:
                dic[asn] = {}
            if prefix not in dic[asn]:
                dic[asn][prefix] = []
            if path not in dic[asn][prefix]:
                dic[asn][prefix].append(path)


with open('quasi_router.txt', 'w') as f:
    for asn in dic:
        num = 0
        for prefix in dic[asn]:
            num = max(num,len(dic[asn][prefix]))
        f.write(asn+' '+str(num)+'\n')

