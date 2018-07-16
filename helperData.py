import json

def simpan(data,nama):
    json.dump(data,open(nama+'.json','w'))
def buka(nama):
    data = json.load(open(nama+'.json','r'))
    return data