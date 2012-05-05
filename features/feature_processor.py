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

def language_converter(f):
    if len(f)==0:
        return 0
    f = sorted(f, key=lambda x: x[-1]) 
    return float(f[0][2])

def dta_converter(f):
    if f:
        return 0
    else:
        return 1

DEFAULT_CONVERTERS = {type(None): nonetype_converter,
              float: float_converter,
              long: long_converter,
              int: int_converter,
              datetime.datetime: dt_converter,
              str: str_converter, 
              decimal.Decimal: dec_converter}

SPECIAL_CONVERTERS = {'languages': language_converter,
                      'directions_to_address': dta_converter}

class Converter(object): 

    @classmethod
    def convert(cls, field_name, field_dct):
        converted = []
        field_type = field_dct['field_type']
        field_data = field_dct['field_data']
        if field_name in SPECIAL_CONVERTERS:
            return SPECIAL_CONVERTERS[field_name](field_data)
        else:
            try:
                return DEFAULT_CONVERTERS[type(field_data)](field_data)
            except KeyError:
                print field_name, field_type, type(field_data)

if __name__ == "__main__":
    test = cPickle.load(open('db_query_example.pkl', 'rb'))
    types = set([])
    for f in test:
        types.add(type(f))
    c = Converter()
    print c.convert(test)
