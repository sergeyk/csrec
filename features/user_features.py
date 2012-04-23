import cPickle
import numpy as np
import bucketizer

class FeatureGetter():
    
    def __init__(self):
        self.load_user_features_pkl()

    def load_user_features_pkl(self):
        print 'loading user data...'
        self.user_data = cPickle.load(open('user_data.pkl', 'rb'))
        print 'data for %s users loaded' % (len(self.user_data))

    def get_features(self, user_id, host_id, req_id):
        output = []
        user_features = self.user_data[user_id]
        host_features = self.user_data[host_id]
        for i in range(len(user_features)):
            u_i = user_features[i]
            h_i = host_features[i]
            if u_i == h_i:
                output.append(1)
            else:
                output.append(0)
        return np.array(output)

def test():
    fg = FeatureGetter()
    print fg.get_features(907345, 907345, 1)

if __name__ == "__main__":
    test()
    
