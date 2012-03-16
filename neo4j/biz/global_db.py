import os
os.environ['NEO4J_PYTHON_JVMARGS'] = '-Xms128M -Xmx4G' 
# CHANGE -Xmx4G to -Xmx512M if you don't have 4 gigs of ram!
from neo4j import GraphDatabase, INCOMING, Evaluation
DATABASE = None

def DB():
    global DATABASE
    return DATABASE


def db_initialized(db_dir):
    return os.path.exists(db_dir)


def shutdown_db():
    global DATABASE
    DATABASE.shutdown()


def set_db(db):
    global DATABASE
    DATABASE = GraphDatabase(db)


def create_new_netflix_db(db_name='db'):
    global DATABASE
    print db_name
    DATABASE = GraphDatabase(db_name)
    with DATABASE.transaction:
        DATABASE.reference_node['label'] = 'reference_node'
        users = DATABASE.node(label='users subreference')
        items = DATABASE.node(label='items subreference')
        global_vars = DATABASE.node(label='global_vars subreference')
        DATABASE.reference_node.USERS(users)['label'] = 'USERS'
        DATABASE.reference_node.ITEMS(items)['label'] = 'ITEMS'
        DATABASE.reference_node.GLOBALS(global_vars)['label'] = 'GLOBAL VARS'

        user_idx = DATABASE.node.indexes.create('users')
        item_idx = DATABASE.node.indexes.create('items')
