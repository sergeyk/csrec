from nlp.extraction import interest_extractor

#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys, os
import cPickle
from mpi.mpi_imports import *

extractor = interest_extractor.InterestExtractor()

def extract_interests(interests_text):
    interests = extractor.extract(interests_text)
    return interests

def print_accepted_interests(cursor):
    list_of_tups = []
    id_dct = {}
        #"ps.description, ps.interests, ps.music_movies_books, ps.people_i_enjoy, " + \
        #"ph.description, ph.interests, ph.music_movies_books, ph.people_i_enjoy " + \
    sql_cmd = "select "+ \
        "ps.user_id, ps.interests, " + \
        "ph.user_id, ph.interests " + \
        "from couchrequest as r inner join (user_profile as ps, user_profile as ph) " + \
        "on (r.surf_user_id=ps.user_id and r.host_user_id=ph.user_id) " + \
        "group by ph.user_id;"
    print sql_cmd
    cur.execute(sql_cmd)
    results = (cur.fetchall())
    total = len(results)
    for i in range(comm_rank, total, comm_size):
        result = results[i]
        s_id = result[0]
        if s_id not in id_dct:
            s_interests = extract_interests(result[1])
            id_dct[s_id] = s_interests 
        h_id = result[2]
        if h_id not in id_dct:
            h_interests = extract_interests(result[3])
            id_dct[h_id] = h_interests
        list_of_tups.append((s_id, h_id))
        completed += 1
        print 'completed %s/%s' % (completed, total/comm_size)
    cPickle.dump(list_of_tups, open('accepted_pairs.pkl.%s' % (comm_rank), 'wb'))
    cPickle.dump(id_dct, open('id_interest_dct.pkl.%s' % (comm_rank), 'wb'))

con = None
username = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASS']

try:

    con = mdb.connect('localhost', username, 
        password, 'csrec');

    cur = con.cursor()
    print_accepted_interests(cur)
        
except mdb.Error, e:
  
    print 'Error %d: %s' % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()
