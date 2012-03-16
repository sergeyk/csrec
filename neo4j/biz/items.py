from global_db import *


class Items(object):

    @classmethod
    def get_items_subreference(cls):
        return DB().reference_node.ITEMS.single.end

    @classmethod
    def get_item_by_id(cls, item_id):
        item_idx = cls.get_items_id_index()
        l = item_idx['item_id'][item_id]
        return item_idx['item_id'][item_id].single

    @classmethod
    def get_items_id_index(cls):
        return DB().node.indexes.get('items')

    @classmethod
    def create_item(cls, item_id):
        item_id = int(item_id)
        new_item = DB().node(item_id=item_id,
                             label='item '+str(item_id))
        new_item.INSTANCE_OF(cls.get_items_subreference())
        item_idx = cls.get_items_id_index()
        item_idx['item_id'][item_id] = new_item
        return new_item

    @classmethod
    def ensure_item_created(cls, item_id):
        item_node = cls.get_item_by_id(item_id)
        if item_node:
            return item_node
        else:
            with cls.gettransaction():
                return create_item(item_id)

    @classmethod
    def get_item_bias(cls, item_id):
        """Returns b_i"""
        return cls.get_item_by_id(item_id)['bias']

    @classmethod
    def set_item_bias(cls, item_id, value):
        """Set b_i"""
        item = cls.get_item_by_id(item_id)
        with cls.gettransaction():
            item['bias'] = value

    @classmethod
    def set_weight(cls, item1_id, item2_id, value):
        """Set edge weight w_ij"""
        item_i = cls.get_item_by_id(item1_id)
        item_j = cls.get_item_by_id(item2_id)

        # Create the relationship between user and item
        relationship = cls.ensure_edge_between_items(item1_id, item2_id)
        with cls.gettransaction():
            relationship['weight'] = value
        
    @classmethod
    def get_weight(cls, item1_id, item2_id):
        """Returns edge weight w_ij"""
        return cls.get_edge_between_items(item1_id, item2_id)['weight']

    @classmethod
    def set_item_knn(cls, item_id, knn):
        """
        Input: knn is a list of tuples (similarity, id).
        Usage: bl.set_item_knn("3810", [(1, '3811')])
        """

        item = cls.get_item_by_id(item_id)
        for neighbor in knn:
            rel = cls.ensure_edge_between_items(item_id, neighbor[1])
            with cls.gettransaction():
                rel['similarity'] = neighbor[0]
    
    @classmethod
    def get_item_knn(cls, item_id):
        related_items = []
        item = cls.get_item_by_id(item_id)
        for related_to_edge in item.RELATED_TO:
            if related_to_edge.start['item_id'] == item_id:
                related_item = related_to_edge.end
            else:
                related_item = related_to_edge.start
            related_items.append(related_item['item_id'])
        return related_items

    
    @classmethod
    def get_similarity_between_items(cls, item1_id, item2_id):
        return cls.get_edge_between_items(item1_id, item2_id)['similarity']

    @classmethod
    def get_edge_between_items(cls, item1_id, item2_id):
        item1 = cls.get_item_by_id(item1_id)
        for related_to_edge in item1.RELATED_TO:
            start_id = related_to_edge.start['item_id']
            end_id = related_to_edge.end['item_id']
            if (item1_id == start_id and item2_id == end_id)\
                    or (item2_id == start_id and item1_id == end_id):
                return related_to_edge

    @classmethod
    def ensure_edge_between_items(cls, item1_id, item2_id):
        edge = cls.get_edge_between_items(item1_id, item2_id)
        if edge:
            return edge
        else:
            with cls.gettransaction():
                rel = cls.get_item_by_id(item1_id)\
                    .RELATED_TO(cls.get_item_by_id(item2_id))
                rel['label'] = 'related_to'
            return rel


    @classmethod
    def get_all_item_ids(cls):
        item_ids = []
        for instance_edge in cls.get_items_subreference().INSTANCE_OF:
            item = instance_edge.start
            item_ids.append(item['item_id'])
        return item_ids

