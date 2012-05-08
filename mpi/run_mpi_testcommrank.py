
import os
import os.path
import numpy as np
from mpi.mpi_imports import *
import time 

def run():
  time.sleep(comm_rank*2)
  print comm_rank, comm_size, os.system('uname -a')
  
 
     
if __name__=='__main__':
  run()
