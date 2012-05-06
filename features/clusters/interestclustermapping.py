import csv

def get_mapping():
    igraph = csv.reader(open("igraph.csv", "rb"))
    mapping = {}
    for data in igraph:
        try:
            mapping[data[0]] = int(data[1])
        except:
            print "if its not the clusterid we dont care"
    return mapping

class InterestClusterMap(object):
    
    def __init__(self):
        self.mapping = get_mapping()

    def get_cluster_id(self, interest_name):
        return self.mapping.get(interest_name, -1)

if __name__=='__main__':
    m = get_mapping()
    print m
    
