import unittest
from biz.business_logic import BusinessLogic as bl
from learning import learn as lrn
from learning import util as lu
from learning import update_functions as uf
from tests.framework import basic_test


class TestBasicLearning(basic_test.BasicTest):

    def test_sanity_compute_item_knn(self):
        bl.set_lambda(2, 1.0)
        print lu.compute_and_set_items_knn(\
            lu.shrunk_pearson_correlation, 2)
        self.assertTrue(True)

    def test_sanity_shrunk_pearson_correlation(self):
        bl.set_lambda(2, 1.0)
        lu.shrunk_pearson_correlation(3810, 3811)
        self.assertTrue(True)

    def test_update_user_bias_1(self):
        bl.set_user_bias(1, 0)
        bl.set_learning_rate(0.5)
        bl.set_lambda(4, 0.25)
        uf.update_user_bias(1, 1)
        self.assertEqual(bl.get_user_bias(1), 0.5)
        uf.update_user_bias(1, 1)
        self.assertEqual(bl.get_user_bias(1), 0.9375)
        uf.update_user_bias(1, 0)
        self.assertEqual(bl.get_user_bias(1), 0.8203125)
        uf.update_user_bias(1, -1)
        self.assertEqual(bl.get_user_bias(1), 0.2177734375)

    def test_update_user_bias_2(self):
        bl.set_user_bias(1, 2)
        bl.set_learning_rate(0.5)
        bl.set_lambda(4, 1)
        uf.update_user_bias(1, 1)
        self.assertEqual(bl.get_user_bias(1), 1.5)

    def test_update_item_bias_1(self):
        bl.set_item_bias(3810, 1)
        bl.set_learning_rate(0.5)
        bl.set_lambda(4, 1)
        uf.update_item_bias(3810, 1)
        self.assertEqual(bl.get_item_bias(3810), 1)

    def test_update_item_bias_2(self):
        bl.set_item_bias(3810, 0)
        bl.set_learning_rate(0.5)
        bl.set_lambda(4, 0.25)
        uf.update_item_bias(3810, 1)
        self.assertEqual(bl.get_item_bias(3810), 0.5)
        uf.update_item_bias(3810, 1)
        self.assertEqual(bl.get_item_bias(3810), 0.9375)
        uf.update_item_bias(3810, 0)
        self.assertEqual(bl.get_item_bias(3810), 0.8203125)
        uf.update_item_bias(3810, -1)
        self.assertEqual(bl.get_item_bias(3810), 0.2177734375)

    def test_update_weights(self):
        bl.set_item_knn(3810, [(1, 3811)])
        bl.set_global_avg(10)
        bl.set_learning_rate(0.5)
        bl.set_lambda(4, 1)
        bl.set_user_bias(1, 1)
        bl.set_item_bias(3811, 1)
        bl.set_weight(3810, 3811, 1)
        uf.update_weights(1, 3810, 1)
        self.assertEqual(bl.get_weight(3810,3811), -4.5)

    def test_make_prediction(self):
        bl.set_item_knn(3810, [(1, 3811)])
        bl.set_global_avg(10)
        bl.set_learning_rate(0.5)
        bl.set_user_bias(1, 1)
        bl.set_item_bias(3810, 1)
        bl.set_item_bias(3811, 1)
        bl.set_weight(3810, 3811, 1)
        self.assertEqual(lrn.make_prediction(1, 3810), 2)


if __name__ == '__main__':
    basic_test.BasicTest.main()
