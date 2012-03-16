from global_db import *

class Users(object):

    @classmethod
    def get_users_subreference(cls):
        return DB().reference_node.USERS.single.end

    @classmethod
    def get_user_by_id(cls, user_id):
        user_idx = cls.get_users_id_index()
        return user_idx['user_id'][user_id].single

    @classmethod
    def get_users_id_index(cls):
        return DB().node.indexes.get('users')

    @classmethod
    def create_user(cls, user_id):
        user_id = int(user_id)
        new_user = DB().node(user_id=user_id,
                             label='user ' + str(user_id))
        new_user.INSTANCE_OF(cls.get_users_subreference())
        user_idx = cls.get_users_id_index()
        user_idx['user_id'][user_id] = new_user
        return new_user

    @classmethod
    def ensure_user_created(cls, user_id):
        user_node = cls.get_user_by_id(user_id)
        if user_node:
            return user_node
        else:
            with cls.gettransaction():
                return create_user(user_id)

    @classmethod
    def get_user_bias(cls, user_id):
        """Returns b_u"""
        return cls.get_user_by_id(user_id)['bias']

    @classmethod
    def set_user_bias(cls, user_id, value):
        """Set b_u"""
        user = cls.get_user_by_id(user_id)
        with cls.gettransaction():
            user['bias'] = value

    @classmethod
    def get_all_user_ids(cls):
        user_ids = []
        for instance_edge in cls.get_users_subreference().INSTANCE_OF:
            user = instance_edge.start
            user_ids.append(user['user_id'])
        return user_ids

