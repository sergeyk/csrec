import unittest
from parsing import parseNetflix
from biz import global_db
from tests.framework import basic_test


class TestBasicDBImport(basic_test.BasicTest):

    num_movies = 40 # None = all of them
    num_ratings_per_movie = 40 #float('inf')

    @classmethod
    def setUpClass(cls):
        if not global_db.db_initialized(cls.get_db_dir()):
            global_db.create_new_netflix_db(cls.get_db_name())
        parseNetflix.parse_netflix_data(cls.get_data_dir(), 
                                        cls.num_movies, 
                                        cls.num_ratings_per_movie) 

    def test_dummy(self):
        """We're just testing the setup class"""
        self.assertTrue(True)

    @classmethod
    def get_data_dir(cls):
        return '/training_set'

if __name__ == '__main__':
    basic_test.BasicTest.main()
