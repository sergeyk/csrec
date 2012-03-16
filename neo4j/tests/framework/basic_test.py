from optparse import OptionParser
import unittest
import os, sys
from biz import global_db
from parsing import parseNetflix
from biz.business_logic import BusinessLogic as bl
from biz.batch_insertion import BatchInserter as bi
import shutil


class BasicTest(unittest.TestCase):
    options = None

    @classmethod
    def main(cls):
        global OPTIONS
        parser = OptionParser()
        parser.add_option("-k", "--keep",
                          action="store_true", dest="keep_db", default=False,
                          help="Use this flag to keep the output database on disk")
        (cls.options, args) = parser.parse_args()
        del sys.argv[1:]
        unittest.main()

    @classmethod
    def get_data_dir(cls):
        return '/basic_test_data'

    @classmethod
    def get_db_name(cls):
        return 'db'

    @classmethod
    def get_db_dir(cls):
        return os.getcwd()+'/'+cls.get_db_name()

    @classmethod
    def setUpClass(cls):
        if not global_db.db_initialized(cls.get_db_dir()):
            global_db.create_new_netflix_db(cls.get_db_name())
        parseNetflix.parse_netflix_data(cls.get_data_dir())        

    @classmethod
    def tearDownClass(cls):
        global_db.shutdown_db()
        if not cls.options or not cls.options.keep_db:
            shutil.rmtree(cls.get_db_dir())
        bi.reset()
