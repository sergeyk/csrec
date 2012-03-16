import unittest
from biz.business_logic import BusinessLogic as bl
from learning import learn as lrn
from learning import util as lu
from tests.framework import basic_test

class TestKNN(basic_test.BasicTest):

    def test_sanity_compute_item_knn(self):
        bl.set_lambda(2, 0)
        print lu.compute_and_set_items_knn(\
            lu.shrunk_pearson_correlation, 9)
        self.assertEqual(bl.get_similarity_between_items(6,  7), 93)
        self.assertEqual(bl.get_similarity_between_items(6,  10), -37)
        self.assertEqual(bl.get_similarity_between_items(5,  9), 96)
        self.assertEqual(bl.get_similarity_between_items(8,  2), -24)
        self.assertEqual(bl.get_similarity_between_items(1,  4), 92)
        self.assertEqual(bl.get_similarity_between_items(3,  2), -20)
    
    def test_user_node_creation(self):
        self.assertEqual(len(bl.get_all_item_ids()), 10)
        self.assertEqual(len(bl.get_all_user_ids()), 10)

    @classmethod
    def get_data_dir(cls):
        return '/knn_test_data'

if __name__ == '__main__':
    basic_test.BasicTest.main()
