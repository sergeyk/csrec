#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys, os

def print_profile(attr_lst):
    attr_order = ['Interests']
    for i in range(len(attr_order)):
        print '==', attr_order[i], '=='
        print attr_lst[i]

def print_accepted_interests(cursor):
        #"ps.description, ps.interests, ps.music_movies_books, ps.people_i_enjoy, " + \
        #"ph.description, ph.interests, ph.music_movies_books, ph.people_i_enjoy " + \
    sql_cmd = "select "+ \
        "ps.interests, " + \
        "ph.interests " + \
        "from couchrequest as r inner join (user_profile as ps, user_profile as ph) " + \
        "on (r.surf_user_id=ps.user_id and r.host_user_id=ph.user_id) " + \
        "where r.status='Y' " + \
        "group by ph.user_id " + \
        "limit 10;"
    print sql_cmd
    cur.execute(sql_cmd)
    results = (cur.fetchall())
    for result in results:
        result = list(result)
        split = len(result)/2
        print 'Surfer>>>>>>>>>>>>>>>>>>>>>>'
        print_profile(result[:split])
        print 'Host<<<<<<<<<<<<<<<<<<<<<<<<'
        print_profile(result[split:])
        print '--------------------------------------------------------\n\n\n'


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
