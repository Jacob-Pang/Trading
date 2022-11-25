# cython: language_level = 3
# distutils: language = c++

cimport cython
from libcpp.unordered_map cimport unordered_map
from cython.operator cimport dereference, postincrement

# Importing cppclass 
cdef extern from "Balance.h":
    cdef cppclass Balance:
        Balance(long long, double) except +
        long long get_key() const
        double get_size() const
        double get_value(double) const
        void integrate_into_balances(unordered_map[long long, Balance*] &)

cdef extern from "CFDBalance.h":
    cdef cppclass CFDBalance (Balance):
        CFDBalance(long long, long long, double, double) except +
        long long get_key() const
        double get_size() const
        double get_value(double) const
        void integrate_into_balances(unordered_map[long long, Balance*]&)

cdef class Balances:
    cdef dict keys_to_tickers
    cdef unordered_map[long long, Balance*] balances

    # Getters
    cpdef double get_size(self, str ticker)
    cpdef double get_value(self, str ticker, double price)
    
    # Mutators
    cpdef void add_balance(self, str ticker, double size)
    cpdef void add_cfd_balance(self, str ticker, str settlement_ticker, double size, double entry_price)
    cpdef void assimilate(self, Balances other)
