#Training params
lambdas = [[.01, .01]]
memory_for_personalized_parameters = 20 #512.0 # memory in MB if using personalized SGD learning  
train_percentage = 0.002 # Dependent on machines in future min:10%, 2nodes->80%
outer_iterations = 1 #10
nepoches = 0.01 #10
alpha = 100.0
beta = 0.001 #0.01
verbose = False
personalization = False # no hashing -> faster
rhostsize = 1000000
just_winning_sets = False
testing = False # should be false to get the full data set
train_dirname = '/home/ron/csrec/params/'
god_mode = False

#Testing params
test_dirname = train_dirname	
test_filename = 'parameters_lwin_0.010000_lrej_0.010000_testing_0_personalized_0_numsets_3247_outerit_1_nepoches_0.pkl'
test_percentage = .002
baseline = False
allow_rejects = True
memory_for_personalized_parameters = 500
