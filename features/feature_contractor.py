import cPickle
import datetime
import numpy as np
import decimal

def nonetype_converter(f):
    return 0

def float_converter(f):
    return f

def long_converter(f):
    return float(f)

def int_converter(f):
    return float(f)

def str_converter(f):
    return float(hash(f))

def dt_converter(f):
    dt_ord = float(f.toordinal())
    return dt_ord

def dec_converter(f):
    return float(f)

CONVERTERS = {type(None): nonetype_converter,
              float: float_converter,
              long: long_converter,
              int: int_converter,
              datetime.datetime: dt_converter,
              str: str_converter, 
              decimal.Decimal: dec_converter}

class Converter(object):
    
    def convert(self, f_lst):
        converted = []
        for f in f_lst:
            converted.append(CONVERTERS[type(f)](f))
        return np.array(converted)

if __name__ == "__main__":
    test = cPickle.load(open('db_query_example.pkl', 'rb'))
    types = set([])
    for f in test:
        types.add(type(f))
    c = Converter()
    print c.convert(test)
