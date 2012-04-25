import _mysql as sql
import datetime
import numpy as np
import sklearn.cluster
from IPython import embed
import time
import cPickle
import os
from Sqler import *
from mpi4py import MPI

comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank()
comm_size = comm.Get_size()
 
def swap_inds(arr, a, b):
  arr[np.where(arr==a)[0]] = -1
  arr[np.where(arr==b)[0]] = a
  arr[np.where(arr==-1)[0]] = b

def rename_clusters(cluster):
  smallest_ind = 0
  last_ind = -1
  for idx in range(cluster.shape[0]):
    index = cluster[idx]
    if not index == last_ind:
      if index < smallest_ind:
        raise RuntimeError("Well...What? they should be ordered!")
      # swap vals
      swap_inds(cluster, smallest_ind, index)
      last_ind = smallest_ind
      smallest_ind+=1      

def split_requests(reqs, cluster):
  req_sets = []
  req_set = []
  curr_cl = cluster[0] 
  
  for idx, req in enumerate(reqs):
    cl = cluster[idx]
    if cl == curr_cl:
      req_set.append(req)
    else:
      req_sets.append(req_set)
      req_set = [req]
      curr_cl = cl
      
  req_sets.append(req_set)
  return req_sets
  
def clusterize(sq, reqs):
  # TODO: This can definitely be sped up!
  # ========= Cluster Responses =============
  rsps_raw = [sq.convert_datetime(x[4]) for x in reqs]
  
  min_rsp = np.min(rsps_raw)
  rsps = [int((x-min_rsp).total_seconds()) for x in rsps_raw]
  rsps_arr = np.asmatrix(rsps).T
  max_rsp = np.max(rsps_arr)
  if max_rsp == 0:
    return [reqs]
  rsps_arr = rsps_arr/float(max_rsp)
  ms = sklearn.cluster.mean_shift(np.asarray(rsps_arr), 60*30/float(max_rsp))
  
  cluster = ms[1]
  rename_clusters(cluster)
  
  # Get reqest sets
  req_sets = split_requests(reqs, cluster)
  
  try:
    assert (len(reqs) == sum(len(x) for x in req_sets))
  except:
    embed()
  return req_sets  

def get_sessions(lower, upper, force=False):
  sq = Sqler()
  sq_write = Sqler()
  table = 'couchrequest'  
  
  t = time.time() 
  res = sq.get_requests(table,lower,upper)
  t -= time.time()
  print 'db query took %f sec'%(-t)  
      
  # format all_rqsts: host_user_id, status, surf_user_id, id, rmd
  last_hid = -1
  reqs = []
  comp_set_id = 0
  t = time.time()
  last_disp_time = time.time() 
  count = 0
  complain_filename = 'complain_file'
  rows = res.fetch_row(11000000,0)
  print 'read all rows'
  num_rows = len(rows)
  print 'there are %d rows'%num_rows
#  cPickle.dump(rows, open('dump_rows_'+comm_rank,'r'))
#  return
  
  for rowdex in range(num_rows):
    row = rows[rowdex]
    count += 1
    
    hid = row[0]
    if not last_hid == hid and not last_hid == -1:
      # we have a new host
      print 'at host %s'%last_hid
      # do something with reqs
      into_next = False
      if len(reqs) == 0:
        reqs.append(row)
      else:
        into_next = True  
    
      t_clus = time.time()
      clus = clusterize(sq_write, reqs)
      t_clus -= time.time()
      
      curr_rqst = "INSERT INTO `competitor_sets2` VALUES"
      
      for cl in clus:        
        for r in cl:
          winner = (r[1] == 'Y')
          curr_rqst += "( "+str(r[3])+" , "+ str(comp_set_id)+" , "+str(last_hid) + \
            " , "+ str(r[2])+" , "+str(int(winner))+ " , '"+str(r[4])+ "', " +str(comm_rank)+" ),"
        comp_set_id += 1
      try:
        sq_write.rqst(curr_rqst[:-1]+";")
      except:
        # What is going on here? print out this request and machine
        cfile = open(complain_filename, 'a')
        complain = '%d: %s\n'%(comm_rank, curr_rqst[:-1]+";")
        cfile.writelines(complain)
        cfile.close()
                        
      reqs = [row]      
    else:
      reqs.append(row)
    
    last_hid = hid
    
  t -= time.time()
  count = comm.reduce(count)
  cfile = open(complain_filename, 'a')
  complain = '%d had %d rows\n'%(comm_rank, count)
  cfile.writelines(complain)
  cfile.close()
  if comm_rank == 0:
    print 'We saw a total of %d line'%(count)  
  return    

if __name__=='__main__':
  
  num_hosts = 845024
  upper = num_hosts/comm_size
  lower = comm_rank*upper
  if comm_rank == comm_size - 1:
    # This is the last machine, why don't we just give it the remaining hosts.
    upper*=2  
  print '%d: %d - %d'%(comm_rank, lower,upper)
  get_sessions(lower, upper, force=True)