import _mysql as sql
import datetime
import Image, ImageDraw
import numpy as np
import sklearn.cluster
from IPython import embed
import time
import cPickle
import os

class Sqler:
  def __init__(self):
    if os.path.exists('/u/vis/'):
      self.db = sql.connect(db='csrec',user='sergeyk',unix_socket='/u/vis/x1/sergeyk/mysql/mysql.sock')#,host='orange4')
    elif os.path.exists('/home/tobibaum/'):    
      self.db = sql.connect(db='CSRec')

  def rqst(self, request, verbose=False):
    t = time.time()
    self.db.query(request)
    t -=time.time()
    
    if verbose:
      print 'db request took %f seconds'%(-t)
    res = self.db.use_result()
    self.res = res
    return res

  def get_row(self, style=1):
    return self.res.fetch_row(1,style)
    
  def get_requests(self, table, lower, upper):    
    res = self.rqst("select couchrequest.host_user_id, status, surf_user_id, id, \
      rmd from (select host_user_id from couchrequest group by host_user_id limit " \
      +str(lower)+","+str(upper)+") as T inner join couchrequest on \
      (couchrequest.host_user_id = T.host_user_id) order by host_user_id, rmd")
    # instead of all at a time fetch  the rows one after the other.
    return res 

  def get_max_depart(self, reqs):
    return np.max([self.convert_datetime(x['date_departure']) for x in reqs])
  
  def get_min_arrive(self, host_id, reqs):
    return np.min([self.convert_datetime(x['date_arrival']) for x in reqs])

  def get_min_request(self, host_id, reqs):
    return np.min([self.convert_datetime(x['rcd']) for x in reqs])

  def get_max_request(self, host_id, reqs):
    return np.max([self.convert_datetime(x['rcd']) for x in reqs])
    
  def convert_datetime(self, timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S')

 
  