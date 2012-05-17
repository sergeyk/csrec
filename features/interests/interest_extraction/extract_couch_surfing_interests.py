from nlp.extraction import interest_extractor

#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys, os
import cPickle
from mpi.mpi_imports import *

global con, cur

extractor = interest_extractor.InterestExtractor()

def extract_interests(interests_text):
    interests = extractor.extract(interests_text)
    return interests

def extract_ids():
    all_ids_set = set([])
    for user_type in ['host_user_id', 'surf_user_id']:
        sql_cmd = "select distinct %s from couchrequest;" % (user_type)
        cur.execute(sql_cmd)
        results = (cur.fetchall())
        for r in results:
            all_ids_set.add(r[0])
    print len(all_ids_set)
    cPickle.dump(list(all_ids_set), open('active_user_ids.pkl', 'wb'))
    
def extract_profiles():
    hits = 0
    attempted = 0
    active_user_ids = cPickle.load(open('active_user_ids.pkl', 'rb'))
    already_done = cPickle.load(open('merged_interest_dct.pkl', 'rb'))
    print 'currently cached ', len(already_done)
    total = len(active_user_ids)
    i_dct = {}
    for i in range(comm_rank, total, comm_size):
        attempted+=1
        user_id = active_user_ids[i]
        if user_id in already_done:
            hits += 1
        else:
            sql_cmd = "select interests from user_profile where user_id=%s;" % (user_id)
            cur.execute(sql_cmd)
            initial_results = cur.fetchall()
            if len(initial_results)==0:
                i_dct[user_id] = []
                continue
            result = initial_results[0]
            interest_text =  result[0]
            i_dct[user_id] = extract_interests(interest_text)
        if attempted % 1000 == 0:
            print hits,'/',attempted
            print '%s completed %s/%s' % (comm_rank, attempted, total/comm_size)
    cPickle.dump(i_dct, open("id_interest_dct_%s.pkl" % (comm_rank), "wb"))

def init_db():
    global con, cur
    username = os.environ['MYSQL_USER']
    password = os.environ['MYSQL_PASS']

    try:
        con = mdb.connect('localhost', username, 
                          password, 'csrec');

        cur = con.cursor()        
    except mdb.Error, e:
  
        print 'Error %d: %s' % (e.args[0],e.args[1])
        sys.exit(1)
    

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-i", action="store_true", dest="gen_id", 
                      help="generate ids")
    parser.add_option("-p", action="store_true", dest="gen_p", 
                      help="get profiles")
    (options, args) = parser.parse_args()

    print options, args
    
    init_db()
    
    if options.gen_id:
        extract_ids()
    elif options.gen_p:
        extract_profiles()
    else:
        parser.print_help()



