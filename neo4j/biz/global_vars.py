from global_db import *


class GlobalVars:

    @classmethod
    def get_lambda(cls, num):
        """Returns lambdas"""
        return cls.get_globals_subreference()['lambda '+ str(num)]

    @classmethod
    def set_lambda(cls, num, value):
        """Sets lambdas"""
        with cls.gettransaction():
            lambda_name = 'lambda '+ str(num)
            cls.get_globals_subreference()[lambda_name] = value

    @classmethod
    def get_learning_rate(cls):
        """Returns learning rate"""
        return cls.get_globals_subreference()['learning_rate']

    @classmethod
    def set_learning_rate(cls, value):
        """Sets learning rate"""
        with cls.gettransaction():
            cls.get_globals_subreference()['learning_rate'] = value

    @classmethod
    def get_global_avg(cls):
        """Returns global avg ratings"""
        return cls.get_globals_subreference()['avg']

    @classmethod
    def set_global_avg(cls, value):
        """Set global avg ratings"""
        with cls.gettransaction():
            cls.get_globals_subreference()['avg'] = value

    @classmethod
    def get_globals_subreference(cls):
        return cls.get_reference_node().GLOBALS.single.end
