import time

def safebarrier(comm, tag=0, sleep=0.01):
   '''
   This is a better mpi barrier than MPI.comm.barrier(): the original barrier
   may cause idle processes to still occupy the CPU, while this barrier waits
   without occupying any CPU.
   '''
   size = comm.Get_size()
   if size == 1:
       return
   rank = comm.Get_rank()
   mask = 1
   while mask < size:
       dst = (rank + mask) % size
       src = (rank - mask + size) % size
       req = comm.isend(None, dst, tag)
       while not comm.Iprobe(src, tag):
           time.sleep(sleep)
       comm.recv(None, src, tag)
       req.Wait()
       mask <<= 1
