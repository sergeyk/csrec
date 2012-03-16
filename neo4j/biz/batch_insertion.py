from global_db import *
from business_logic import BusinessLogic as bl


class BatchInserter(object):
    
    batch_mode = False
    written_users = {}
    written_items = {}
    item_nodes = set([])
    user_nodes = set([])
    item_item_edges = {}
    user_item_edges = {}
    item_nodes_objects = {}
    user_node_objects = {}

    @classmethod
    def debug_print(cls):
        print cls.item_nodes
        print cls.user_nodes
        print cls.item_item_edges
        print cls.user_item_edges        
        
    @classmethod
    def reset(cls):
        cls.batch_mode = False
        cls.written_users = {}
        cls.written_items = {}
        cls.item_nodes = set([])
        cls.user_nodes = set([])
        cls.item_item_edges = {}
        cls.user_item_edges = {}
        cls.item_nodes_objects = {}
        cls.user_node_objects = {}

    @classmethod
    def insert_user_node(cls, user_id):
        if user_id not in cls.written_users:
            return cls._insert_node(cls.user_nodes, user_id)
        else:
            return {}

    @classmethod    
    def insert_item_node(cls, item_id):
        return cls._insert_node(cls.item_nodes, item_id)

    @classmethod
    def _insert_node(cls, index, node_id):
        index.add(node_id)
        return {}

    @classmethod
    def insert_user_item_edge(cls, user_id, item_id, weight=None):
        return cls._insert_edge(cls.user_item_edges, user_id, item_id, weight, False)

    @classmethod # This method is unused. The netflix dataset doesn't include these
    def insert_item_item_edge(cls, item1_id, item2_id):
        if start < end:
            first_key = start
            second_key = end
        else:
            first_key = end
            second_key = start
        return cls._insert_edge(cls.item_item_edges, first_key, second_key, weight)

    @classmethod
    def _insert_edge(cls, index, first_key, second_key, weight, check=True):
        if check and (first_key in index and second_key in index[first_key]):
            return index[first_key][second_key]
        else:
            if first_key not in index:
                index[first_key] = {}
            new_edge = {}
            if weight:
                new_edge['weight'] = weight
            index[first_key][second_key] = new_edge
            return new_edge
    
    @classmethod
    def start_batch_mode(cls):
        cls.batch_mode = True
    
    @classmethod
    def is_batch_mode(cls):
        return cls.batch_mode

    @classmethod
    def end_batch_mode(cls):
        cls.batch_mode = False
    
    @classmethod
    def flush(cls):
        print 'flushing...'
        cls.flush_nodes()
        cls.flush_edges()
        cls.flush_cleanup()

    @classmethod
    def flush_nodes(cls):
        with DB().transaction:
            i = 0
            item_count = len(cls.item_nodes)
            print '%s items' % (item_count)
            for key in cls.item_nodes:
                item_node = bl.create_item(key)
                cls.written_items[key] = item_node
                i+=1
                #print "%s/%s item nodes written" % (i, item_count)
            i = 0
            cls.item_nodes = set([])
            user_count = len(cls.user_nodes)
            print '%s new users' % (user_count)
            for key in cls.user_nodes:
                user_node = bl.create_user(key)
                cls.written_users[key] = user_node
                i+=1
                #print "%s/%s user nodes written" % (i, user_count)
            #cls.written_users = cls.written_users.union(cls.user_nodes)
            cls.user_nodes = set([])
            print 'pushing nodes to disk'

    @classmethod
    def flush_edges(cls):
        with DB().transaction:
            i = 0
            num_users_with_ratings = len(cls.user_item_edges)
            print '%s edges' % (num_users_with_ratings)
            for user, hash2 in cls.user_item_edges.iteritems():
                for item, edge_hash in hash2.iteritems():
                    user_node = cls.written_users[user]
                    item_node = cls.written_items[item]
                    rel = bl.create_edge_between_user_and_item_obj(user_node, item_node)
                    rel['weight'] = edge_hash['weight']
                #print "%s/%s ratings written" % (i, num_users_with_ratings)
                i+=1
            print 'pushing edges to disk'
            cls.user_item_edges = {}

    @classmethod
    def flush_cleanup(cls):
        cls.written_items = {}

