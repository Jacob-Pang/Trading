# cython: language_level = 3
# distutils: language = c++

cimport numpy as np
from libcpp.vector cimport vector

cdef class Orderbook:
    cdef vector[double] bid_prices
    cdef vector[double] bid_sizes
    cdef vector[double] accum_bid_sizes
    cdef vector[double] ask_prices
    cdef vector[double] ask_sizes
    cdef vector[double] accum_ask_sizes
    cdef int timestamp

    # Getters
    cpdef bint empty_bid_orderbook(self)
    cpdef bint empty_ask_orderbook(self)
    cpdef tuple get_bid(self, int entry)
    cpdef tuple get_ask(self, int entry)
    cpdef tuple get_market_bid(self, double funding_value)
    cpdef tuple get_market_ask(self, double funding_value)
    cpdef double get_market_bid_price(self, double order_size)
    cpdef double get_market_ask_price(self, double order_size)

    # Mutators
    cpdef void reset(self)
    cpdef void append_bid(self, double bid_price, double bid_size)
    cpdef void append_ask(self, double bid_price, double bid_size)
