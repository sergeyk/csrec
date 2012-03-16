import numpy as np
import os
from base_business_logic import BaseBusinessLogic
from global_db import *

class BusinessLogic(BaseBusinessLogic):

    @classmethod
    def gettransaction(cls):
        return DB().transaction

    @classmethod
    def get_reference_node(cls):
        return DB().reference_node
