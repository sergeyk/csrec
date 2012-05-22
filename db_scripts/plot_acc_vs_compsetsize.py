import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties



x = [2, 3, 4, 5, 6, 7]
acc_we = [0.3201889, 0.254776, 0.2296939, 0.192957, 0.181492, 0.1647929]
meannrank_we = [0.389160, 0.392635, 0.381877, 0.391875, 0.379403, 0.376959]

acc_random = [0.222566672695, 0.173745859438, 0.143345598497, 0.122226, 0.1068759,  0.0946713602598]
meannrank_random = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

acc_prio1 = [0.193823, 0.146598, 0.116289, 0.097372, 0.085032, 0.072961]
meannrank_prio1 = [0.533915, 0.535218, 0.536135, 0.535289, 0.535151, 0.535681]

acc_prio2 = [0.208183, 0.168060, 0.143343, 0.123378, 0.111070, 0.099510]
meannrank_prio2 = [0.564148, 0.568533, 0.572218, 0.577181, 0.581016, 0.585530]

acc_vouched = [0.218627, 0.179128, 0.153777, 0.134347, 0.120612, 0.108277]
meannrank_vouched = [0.604180, 0.613588, 0.620289, 0.626602, 0.631804, 0.638751]

acc_references = [0.255674, 0.204585, 0.172180, 0.148505, 0.133595, 0.119124]
meannrank_references = [0.461327, 0.460676, 0.459630, 0.460904, 0.460903, 0.462353]

acc_friendlink = [0.256589, 0.205529, 0.173822, 0.151556, 0.136702, 0.121650]
meannrank_friendlink = [0.464200, 0.463655, 0.462455, 0.463532, 0.463151, 0.463878]

acc_references2 = [0.255486, 0.204556, 0.171640, 0.148669, 0.133299, 0.118480]
meannrank_references2 = [0.462622, 0.461567, 0.460356, 0.461158, 0.461046, 0.462371]


'Average Normalized Winner Rank'
'Prediction Accuracy'
plt.plot(x, acc_we, 'r', linewidth=2, label = 'Ours')


plt.plot(x, acc_random, linewidth=2, label = 'Random') 
plt.plot(x, acc_prio1, linewidth=2, label = 'Priority1')
plt.plot(x, acc_prio2,  linewidth=2, label = 'Priority2')
plt.plot(x, acc_vouched,  linewidth=2, label = 'Vouched')
plt.plot(x, acc_references,  linewidth=2, label = 'References')
plt.plot(x, acc_friendlink, linewidth=2, label = 'Friend Links')
plt.plot(x, acc_references2,  linewidth=2, label = 'References to')
#plt.plot(x, acc_theirs, 'k--', label='Random Baseline')
#plt.plot(x, np.array(acc_theirs)-0.02, 'k', label='Priority Baseline')

legend_font_props = FontProperties()
legend_font_props.set_size('medium')
plt.legend(numpoints=1, prop=legend_font_props)

plt.xlabel('Size of Competitor Sets')
plt.ylabel('Prediciton Accuracy')

plt.figure()

plt.plot(x, meannrank_we, 'r', linewidth=2, label = 'Ours')

plt.plot(x, meannrank_random, linewidth=1.5, label = 'Random') 
plt.plot(x, meannrank_prio1, linewidth=1.5, label = 'Priority1')
plt.plot(x, meannrank_prio2,  linewidth=1.5, label = 'Priority2')
plt.plot(x, meannrank_vouched,  linewidth=1.5, label = 'Vouched')
plt.plot(x, meannrank_references,  linewidth=1.5, label = 'References')
plt.plot(x, meannrank_friendlink, linewidth=1.5, label = 'Friend Links')
plt.plot(x, meannrank_references2,  linewidth=1.5, label = 'References to')
#plt.plot(x, acc_theirs, 'k--', label='Random Baseline')
#plt.plot(x, np.array(acc_theirs)-0.02, 'k', label='Priority Baseline')

legend_font_props = FontProperties()
legend_font_props.set_size('medium')
plt.legend(numpoints=1, prop=legend_font_props)

plt.xlabel('Size of Competitor Sets')
plt.ylabel('Average Normalized Winner Rank')


plt.show()