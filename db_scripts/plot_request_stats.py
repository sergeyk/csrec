from competitor_sets.Sqler import *
import matplotlib.pyplot as plt

sq = get_sqler()
res = sq.rqst('select * from rec_sent2users')
res_sent = res.fetch_row(100000,0) 
# num_requests, ppl with this count
sent_tab = np.matrix(res_sent, dtype=int)
# Yes, this is hacked. Deal with it.
plt.loglog(sent_tab[:,0],-np.sort(-sent_tab[:,1],0), label='Surfers (sent)')
plt.xlabel('Number of Requests')
plt.ylabel('Number of Users')
 

res = sq.rqst('select * from rec_rqst2users')
res_rec = res.fetch_row(100000,0)
rec_tab = np.matrix(res_rec, dtype=int)
plt.loglog(rec_tab[:,0],-np.sort(-rec_tab[:,1],0), label='Hosts (received)')
plt.legend()
plt.savefig('requests.png')
plt.show()

