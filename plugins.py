"""
from sympy import isprime
class Filter:
    DECIMAL_FILTER = lambda param: True if type(param) == int or param.isdigit() else False
    EVEN_NUMBER_FILTER = lambda param: True if param % 2 == 0 else False
    ODD_NUMBER_FILTER = lambda param: not Filter.EVEN_NUMBER_FILTER(param)
    PRIME_NUMBER_FILTER = lambda param: isprime(param)
"""