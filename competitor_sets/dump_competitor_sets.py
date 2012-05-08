import _mysql as sql
import datetime
import numpy as np
import sklearn.cluster
import time
import cPickle
import os
from Sqler import *
import shutil
import csrec_paths
from mpi.mpi_imports import *

try:
  from IPython import embed
except:
  'failed to import embed'
   
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
  # 3 Days is the magical number. We expect a mean compset-size of 2.4
  MINUTES_BANDWIDTH = 60*24*3
  # ========= Cluster Responses =============
  rsps_raw = [x[4] for x in reqs]
  
  min_rsp = np.min(rsps_raw)
  rsps = [int((x-min_rsp).total_seconds()) for x in rsps_raw]
  rsps_arr = np.asmatrix(rsps).T
  max_rsp = np.max(rsps_arr)
  if max_rsp == 0:
    return [reqs]
  rsps_arr = rsps_arr/float(max_rsp)
  ms = sklearn.cluster.mean_shift(np.asarray(rsps_arr), 60*MINUTES_BANDWIDTH/float(max_rsp))
  
  cluster = ms[1]
  rename_clusters(cluster)
  
  # Get reqest sets
  req_sets = split_requests(reqs, cluster)
  
  # If a set has several winner....split it maan!
  look_at_that = False
  new_req_sets = []
  pop_indices = []
  for req_idx, req_set in enumerate(req_sets):
    num_winners = sum([r[1] == 'Y' for r in req_set])
    if num_winners > 1:
      # Remove that one and compute new split up ones
      pop_indices.append(req_idx)
      winners = []
      losers = []
      for req in req_set:      
        if req[1] == 'Y':
          winners.append(req)
        else:
          losers.append(req)
          
      # for all winners we want one req_set                  
      for win in winners:
        new_req_sets.append(losers + [win])  
      look_at_that = True
  
  for pop_ind_ind, pop_index in enumerate(np.sort(pop_indices)):    
    req_sets.pop(pop_index-pop_ind_ind)
    
  if look_at_that:
    for req_idx, req_set in enumerate(req_sets):
      num_winners = sum([r[1] == 'Y' for r in req_set])
      if num_winners > 1:
        raise RuntimeError('There are still sets with more than 1 winner :/')
  req_sets += new_req_sets
  return req_sets  

def get_sessions(lower, upper, force=False):
  sq = get_sqler()
  #table = 'couchrequest'
  table = 'couchrequest'    
  
  filename = 'cluss_'+str(comm_rank)
  if os.path.exists(filename) and not force:
    return
  
  t = time.time() 
  res = sq.get_requests(table, lower,upper)
  t -= time.time()
  #print 'db query took %f sec'%(-t)  
      
  last_hid = -1
  reqs = [] 
  #rows = res.fetch_row(11000000,0)
  print 'read all rows'
  #num_rows = len(rows)
  #print 'there are %d rows'%num_rows

  cluss = []
  go_on = True
  rows_at_a_time = 11000
  running_sum = 0
  running_count = 0
  while go_on:
    #print 'read %d more rows'%rows_at_a_time
    rows = res.fetch_row(rows_at_a_time,0)
    num_rows = len(rows)
    if num_rows == 0:
      go_on=False
    for rowdex in range(num_rows):
      row = rows[rowdex]
      
      hid = row[0]
      print '%d is at user %d'%(comm_rank, hid)
      if not last_hid == hid and not last_hid == -1:
        # we have a new host
        #print 'at host %s'%last_hid
        into_next = False
        if len(reqs) == 0:
          reqs.append(row)
        else:
          into_next = True    
        
        try:
          clus = clusterize(sq, reqs)
        except:
          None                
                  
#        running_count += len(clus)
#        running_sum += np.sum([len(x) for x in clus])
#        print 'the mean is %f'%(running_sum/float(running_count))
        #print '%d saw %d clusters for user %d'%(comm_rank, len(clus), last_hid)      
        cluss += clus                              
        reqs = [row]      
      else:
        reqs.append(row)    
      last_hid = hid  
  cPickle.dump(cluss, open(filename,'w'))


def create_sessions():  
  #num_hosts = 845024
  # hmm with the new version it should rather be the max number...let's hope
  # they are kinda equally distributed!
  num_hosts = 3963771
  
  step_size = num_hosts/comm_size 
  upper = (comm_rank+1)*step_size
  lower = comm_rank*step_size
  if comm_rank == comm_size - 1:
    # This is the last machine, why don't we just give it the remaining hosts.
    upper*=2  
  print '%d: %d - %d'%(comm_rank, lower,upper)
  get_sessions(lower, upper, force=False)
  
def compile_sessions():  
  sq = get_sqler()
  first_lines = True  
  comp_set_id = 0
  too_much_count = 0
  # IS THIS SUPPOSE TO BE COMPETITOR SETS OR COMPETITOR SETS 2?
  default_string = "INSERT INTO `competitor_sets2` (`req_id`, `set_id`, \
    `host_id`, `surfer_id`, `winner`, `date`) VALUES "
  index = 1
  write_string = default_string
  max_batch_size = 8000
  last_write=False
  for i in range(20):
    read_cluss = cPickle.load(open('cluss_%d'%i,'r'))
    print 'opened file %d'%i
    ###################
    processed = 1
    for cl_idx, cl in enumerate(read_cluss):        
      for r_idx, r in enumerate(cl):
        if r_idx == len(cl)-1 and cl_idx == len(read_cluss)-1:
          last_write=True
        if not first_lines:
          write_string += ','
        else:
          first_lines=False  
          
        winner = (r[1] == 'Y')
        # in-order: host_user_id, status, surf_user_id, id, rmd
        # out-order: req_id, set_id, host_id, surfer_id, winner, date
        write_string += "( "+str(r[3])+" , "+ str(comp_set_id)+" , "+str(r[0]) + \
            " , "+ str(r[2])+" , "+str(int(winner))+ " , '"+str(r[4])+ "' )"
        index+=1
      #print '%d wrote comp set %d'%(comm_rank, comp_set_id)
        too_much_count += 1      
      if too_much_count > max_batch_size or last_write:
        too_much_count = 0
        #print write_string
        sq.rqst(write_string+';', False)       
        del write_string
        write_string = default_string
        first_lines = True
        processed += max_batch_size
        if (processed % 10000) == 0:
          print '%s processed %s/%s' % (comm_rank, processed, len(read_cluss))        
      comp_set_id += 1        
    ###################  
  
if __name__=='__main__':
  create_sessions()
  safebarrier(comm)
  if comm_rank==0:  
    compile_sessions()
