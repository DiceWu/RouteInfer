import json
# Reading data back
paths = {}
cnt = 0
with open('sanitized_rib.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(' ')
        if len(parts) <= 2:
            continue
        aspath = parts[1:]
        prefix = parts[0]
        if prefix not in paths:
            paths[prefix] = []
        paths[prefix].append(aspath)


with open('paths.json', 'w') as f:
    json.dump(paths,f)
    


