import MySQLdb
import datetime
import Image, ImageDraw
import numpy as np
import sklearn.cluster
#from IPython import embed
import time
import cPickle
import os, sys
from functools import wraps

RON_MODE = False #(os.path.exists('/home/ron'))

class Sqler:
  def __init__(self):
    if False:
      import MySQLdb as mdb
      username = os.environ['MYSQL_USER']
      password = os.environ['MYSQL_PASS']
      try:
        self.db = mdb.connect('localhost', username, 
                          password, 'csrec');

        self.cur = self.db.cursor()
      except mdb.Error, e:
        print e
        sys.exit(1)
    else:
      self.max_length_table = 11000000 # Hmm can this be done somehow nicer?
      if os.path.exists('/u/vis/'):
        self.db = MySQLdb.connect(db='csrec',user='sergeyk',unix_socket='/u/vis/x1/sergeyk/mysql/mysql.sock', host='orange4', port=8081)
      elif os.path.exists('/home/tobibaum/'):    
        self.db = MySQLdb.connect(db='CSRec')
      else:
        username = os.environ['MYSQL_USER']
        password = os.environ['MYSQL_PASS']
        self.db = MySQLdb.connect(db='csrec', 
                                  user=username, passwd=password)

  def rqst(self, request, verbose=False):
    t = time.time()
    self.db.query(request)    
    t -=time.time()
    if RON_MODE:
      self.db.commit()
    if verbose:
      print 'db request took %f seconds'%(-t)
    res = self.db.use_result()
    self.res = res
    return res

  def get_row(self, style=1):
    return self.res.fetch_row(1,style)
  
  def get_all_rows(self, style=1, verbose=False):
    print '\tfetching all rows...'
    t = time.time()
    res = self.res.fetch_row(self.max_length_table, style)
    t -=time.time()
    if verbose:
      print '\tfetching took %f seconds'%(-t)
    return res 
    
  def get_requests(self, table, lower, upper):
    req = "select host_user_id, status, surf_user_id, id, rmd from " + table + \
      " where host_user_id > " + str(lower) + " and host_user_id < " + str(upper) + \
      " order by host_user_id, rmd"    
#    req = "select " + table + ".host_user_id, status, surf_user_id, id, \
#      rmd from (select host_user_id from " + table + " group by host_user_id limit " \
#      +str(lower)+","+str(upper)+") as T inner join " + table + " on \
#      (" + table + ".host_user_id = T.host_user_id) order by host_user_id, rmd"
    res = self.rqst(req)
    # instead of all at a time fetch  the rows one after the other.
    return res 
  
  def get_num_compsets(self, set_type):
    set_type_number_map = {
      'train':1,
      'val':2,
      'test':3
      }
    sql_cmd = ('SELECT count(distinct set_id) FROM `competitor_sets` where train_val_test=%s'
               % set_type_number_map[set_type])
    res = self.rqst(sql_cmd)
    num_compsets = int(res.fetch_row(1,0)[0][0])
    res.fetch_row(10,0)
    return num_compsets

  def get_max_depart(self, reqs):
    return np.max([self.convert_datetime(x['date_departure']) for x in reqs])
  
  def get_min_arrive(self, host_id, reqs):
    return np.min([self.convert_datetime(x['date_arrival']) for x in reqs])

  def get_min_request(self, host_id, reqs):
    return np.min([self.convert_datetime(x['rcd']) for x in reqs])

  def get_max_request(self, host_id, reqs):
    return np.max([self.convert_datetime(x['rcd']) for x in reqs])
    
  def convert_datetime(self, timestring):
    #Ron: it seems like timestring is already a datetime on my computer.
    #return datetime.datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S')
    if RON_MODE:
      return timestring
    else:
      return datetime.datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S')

  
def safe_mysql(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    try:
      return f(*args, **kwds)
    except mdb.OperationalError, e:
      if int(e.args[0]) == 1040:
        base_sleep_time = 1
        sleep_time = random.randint(0,3) + base_sleep_time
        time.sleep(sleep_time)
        print '%s: max connection error, sleeping' % commrank
      else:
        print '\n\n\t\t%s: Error %d: %s\n\n' % (commrank, e.args[0],e.args[1])
        sys.exit(1)
  return wrapper

sqler = Sqler()
def get_sqler():
  return sqler
