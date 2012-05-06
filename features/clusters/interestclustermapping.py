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
    
        
if __name__=='__main__':
    m = get_mapping()
    print m
    
