from Sqler import *
import cPickle

def find_missing_requests(max_rows):
  # Read both databases
  sqA = Sqler()
  sqB = Sqler()
  sqA.rqst("select id from couchrequest order by id")
  sqB.rqst("select req_id from competitor_sets2 order by req_id")
  
  moveB = True
  missing = []
  atrowA = 0
  count = 0
  for _ in range(max_rows):
    rowA = sqA.get_row()
    atrowA += 1
    count += 1
    if rowA == ():
      break
    else:
      reqA = int(rowA[0]['id'])
    if moveB:
      rowB = sqB.get_row()      
      if rowB == ():
        moveB = False
      else:
        reqB = int(rowB[0]['req_id'])
    if count > 500:
      print 'atrow: %d'%atrowA
      count = 0
      
    #print "%d - %d"%(reqA, reqB) 
    if reqA == reqB:
      moveB = True
    else:
      missing.append(reqA)
      moveB = False
  return missing

def chunks(l, n):
  return [l[i:i+n] for i in range(0, len(l), n)]


def write_missing_to_table(missing):
  miss_chunks = chunks(missing,10000)
  sq = Sqler() 
  for miss in miss_chunks:    
    curr_rqst = "INSERT INTO `missing_requests2` VALUES"
    for m in miss:
      curr_rqst += "( "+str(m)+" ),"
    sq.rqst(curr_rqst[:-1]+";")
  

if __name__=='__main__':
  max_rows = 12000000
  missing = find_missing_requests(max_rows)
  cPickle.dump(missing, open('missing_requests2', 'w'))
#  #print missing
  print 'there are %d missing'%len(missing)
  missing = cPickle.load(open('missing_requests2', 'r'))
  write_missing_to_table(missing)
  