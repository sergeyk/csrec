import unittest
from biz.business_logic import BusinessLogic as bl
from tests.framework import basic_test

class TestBasicDB(basic_test.BasicTest):

    def test_item_knn(self):
        bl.set_item_knn(3810, [(1, 3811)])
        self.assertEqual(tuple(bl.get_item_knn(3810)),
                         tuple([3811]))
        self.assertEqual(tuple(bl.get_item_knn(3811)),
                         tuple([3810]))

    def test_get_items_rated_by_user(self):
        self.assertEqual(tuple(bl.get_items_rated_by_user(1)),
                         tuple([3810, 3811]))
        self.assertEqual(tuple(bl.get_items_rated_by_user(2)),
                         tuple([3810, 3811]))
        self.assertEqual(tuple(bl.get_items_rated_by_user(3)),
                         tuple([3810]))

    def test_rating(self):
        bl.set_rating(1, 3810, 3)
        self.assertEqual(bl.get_rating(1, 3810), 3)
    
    def test_common_ratings(self):
        self.assertEqual(tuple(bl.get_common_raters(3810, 3811)),
                         tuple([1, 2]))
                
    def test_user_bias(self):
        bl.set_user_bias(1, 1)
        self.assertEqual(bl.get_user_bias(1), 1)
        bl.set_user_bias(1, 2)
        self.assertEqual(bl.get_user_bias(1), 2)
        bl.set_user_bias(2, 1)
        self.assertEqual(bl.get_user_bias(2), 1)

    def test_item_bias(self):
        bl.set_item_bias(3810, 1)
        self.assertEqual(bl.get_item_bias(3810), 1)
        bl.set_item_bias(3810, 2)
        self.assertEqual(bl.get_item_bias(3810), 2)
        bl.set_item_bias(3811, 2)
        self.assertEqual(bl.get_item_bias(3811), 2)

    def test_lambda(self):
        bl.set_lambda(1, 1)
        self.assertEqual(bl.get_lambda(1), 1)
        bl.set_lambda(2, 1)
        self.assertEqual(bl.get_lambda(2), 1)

    def test_learning_rate(self):
        bl.set_learning_rate(5)
        self.assertEqual(bl.get_learning_rate(), 5)

    def test_global_avg(self):
        bl.set_global_avg(10)
        self.assertEqual(bl.get_global_avg(), 10)

    def test_weight(self):
        bl.set_weight(3810, 3811, 5)
        self.assertEqual(bl.get_weight(3810, 3811), 5)


if __name__ == '__main__':
    basic_test.BasicTest.main()
