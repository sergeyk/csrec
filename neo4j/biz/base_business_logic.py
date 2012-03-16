import numpy as np
import os
import items
import users
import global_vars
from global_db import *

class BaseBusinessLogic(items.Items, 
                        users.Users,
                        global_vars.GlobalVars):
    """ This class is an interface and should NOT be instantiated.
    
    When extending this class, make sure to implement get_transaction()"""

    @classmethod
    def get_items_rated_by_user(cls, user_id):
        items = []
        user = cls.get_user_by_id(user_id)
        for rated_edge in user.RATED:
            item = rated_edge.end
            items.append(item['item_id'])
        return items

    @classmethod
    def get_item_raters(cls, item_id):
        item_node = cls.get_item_by_id(item_id)
        users = []
        for rated_edge in item_node.RATED:
            rater = rated_edge.start
            users.append(rater['user_id'])
        return users

    @classmethod
    def get_rated_knn(cls, user_id, item_id):
        """Returns R^k(u;i)."""
        return set(cls.get_item_knn(item_id)).intersection(\
            set(cls.get_items_rated_by_user(user_id)))

    @classmethod
    def get_ratings_for_item(cls, item_id, users=None):
        output = []
        raters = cls.get_item_raters(item_id)
        for rater in raters:
            if not users or rater in users:
                output.append(cls.get_rating(rater, item_id))
        return output

    @classmethod
    def get_rating(cls, user_id, item_id):
        """Returns r_ui."""
        return int(cls.get_edge_between_user_and_item(user_id, item_id)['weight'])

    @classmethod
    def set_rating(cls, user_id, item_id, value):
        """Set r_ui"""
        user = cls.get_user_by_id(user_id)
        item = cls.get_item_by_id(item_id)

        # Create the relationship between user and item
        relationship = cls.ensure_edge_between_user_and_item(user_id, item_id)
        with cls.gettransaction():
            relationship['weight'] = int(value)

    @classmethod
    def get_common_raters(cls, item1_id, item2_id):
        raters1 = cls.get_item_raters(item1_id)
        raters2 = cls.get_item_raters(item2_id)
        common_raters = np.intersect1d(raters1, raters2)
        return common_raters

    @classmethod
    def get_edge_between_user_and_item(cls, user_id, item_id):
        user = cls.get_user_by_id(user_id)
        for rated_edge in user.RATED:
            if rated_edge.end['item_id'] == item_id:
                return rated_edge

    @classmethod
    def create_edge_between_user_and_item(cls, user_id, item_id):
        return create_edge_between_user_and_item_obj(cls.get_user_by_id(user_id),
                                                     cls.get_item_by_id(item_id))

    @classmethod
    def create_edge_between_user_and_item_obj(cls, user_node, item_node):
        rel = user_node.RATED(item_node)
        rel['label'] = 'rated'
        return rel

    @classmethod
    def create_edge_between_user_and_item_obj(cls, user_node, item_node):
        rel = user_node.RATED(item_node)
        rel['label'] = 'rated'
        return rel

    @classmethod
    def ensure_edge_between_user_and_item(cls, user_id, item_id):
        """Returns the edge as a relationship in the DB."""
        edge = cls.get_edge_between_user_and_item(user_id, item_id)
        if edge:
            return edge
        else:
            with cls.gettransaction():
                cls.create_edge_between_user_and_item(user_id, item_id)

    @classmethod
    def get_reference_node(cls):
        raise NotImplementedError
