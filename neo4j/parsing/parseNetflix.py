import os
import global_paths
from biz.batch_insertion import BatchInserter as bi


def parse_netflix_data(dataset='/training_set', k=None, l=float('inf')):
    bi.start_batch_mode()
    print 'dataset:%s, reading %s ratings from %s movies' % (dataset, l, k)
    #path temporarily set for local machine
    path = global_paths.get_dataset_dir()+dataset

    listing = os.listdir(path)[:k]
    
    listing = sorted(listing)
    
    f = None

    z = 0
    
    flush_interval = 10
    
    for mv_file in listing:
        mv_path = path + '/' + mv_file
        f = open(mv_path)
        print mv_file + '...',
        item_id = f.readline()[:-2]
        line = f.readline()
        bi.insert_item_node(item_id)
        z += 1
        i = 0
        while line != "" and i<l:
            user_id,rating,date = line.strip().split(",")
            line = f.readline()
            bi.insert_user_node(user_id)
            bi.insert_user_item_edge(user_id, item_id, rating)
            i+=1
        print 'done %s/%s' % (z, k)
        if z % flush_interval == 0:
            bi.flush()
    bi.flush()
