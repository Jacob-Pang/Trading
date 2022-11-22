# cython: language_level = 3
# distutils: language = c++

cimport cython
from libcpp.unordered_map cimport unordered_map
from cython.operator cimport dereference, postincrement

cdef class Balances:
    cdef dict hashkey_to_tickers
    cdef unordered_map[long long, double] amounts

    # Getters
    cdef double get_amount(self, long long ticker_hashkey)
    cpdef double get(self, str ticker)
    cpdef double get_net_value(self, dict ticker_values)
    
    # Mutators
    cdef bint add_amount(self, long long ticker_hashkey, double amount)
    cpdef void add(self, str ticker, double amount)
    cpdef void assimilate(self, Balances other)
