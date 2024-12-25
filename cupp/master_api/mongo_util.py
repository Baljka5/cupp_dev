from pymongo import MongoClient


def get_bizloc_tp_by_cd(bizloc_cd):
    client = MongoClient('mongodb://10.10.90.230:27017/')
    db = client['nubia_db']
    collection = db['bgf_hq_bizloc_mst']
    bizloc = collection.find_one({'bizloc_cd': bizloc_cd})
    client.close()
    return bizloc['bizloc_tp'] if bizloc else None
