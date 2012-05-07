import csv, os

def get_mapping():
    igraph = csv.reader(open(os.path.dirname(os.path.realpath(__file__))+"/igraph.csv", "rb"))
    mapping = {}
    skip = True
    for data in igraph:
        if not skip:
            mapping[data[0]] = int(data[1])+1
        skip = False
    return mapping

class InterestClusterMap(object):
    
    def __init__(self):
        self.mapping = get_mapping()

    def get_cluster_id(self, interest_name):
        return self.mapping.get(interest_name, 0)

if __name__=='__main__':
    m = get_mapping()
    print m
    
