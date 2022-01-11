import json
# Reading data back
ip2as = {}

with open('sanitized_rib.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(' ')
        if len(parts) <= 2:
            continue
        prefix = parts[0]
        desas = parts[-1]
        if prefix not in ip2as:
            ip2as[prefix] = []
        if desas not in ip2as[prefix]:
            ip2as[prefix].append(desas)

with open('ip2as.json', 'w') as f:
    json.dump(ip2as,f)  

