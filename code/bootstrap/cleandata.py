import json
import os

paths = set()

file = open('BGPdata/example.txt','r')
for line in file:
    line = line.strip()
    asn_list = line.split(" ")[1:]
    # remove prepended ASes
    asn_list = [v for i, v in enumerate(asn_list)
        if i == 0 or v != asn_list[i-1]]
    asn_set = set(asn_list)
    # remove poisoned paths with AS loops
    if len(asn_set) == 1 or not len(asn_list) == len(asn_set):
        continue
    else:
        for asn in asn_list:
            try:
                asn = int(asn)
            except:
                break
            # reserved ASN
            if asn == 0 or asn == 23456 or asn >= 394240 \
                or (61440 <= asn <= 131071) \
                or (133120 <= asn <= 196607)\
                or (199680 <= asn <= 262143)\
                or (263168 <= asn <= 327679)\
                or (328704 <= asn <= 393215):
                break
        else:
            paths.add(line.split(" ")[0]+" " + " ".join(asn_list))
        continue
outfile = open('sanitized_rib.txt', 'w')
for path in paths:
    outfile.write(path + '\n')
outfile.close()
