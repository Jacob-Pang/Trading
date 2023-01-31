# cython: language_level = 3
# distutils: language = c++
cimport numpy as np

from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from pyutils.array_queue.float_array_queue cimport FloatArrayQueue, FloatArrayIterator
from pyutils.array_queue.int_array_queue cimport IntArrayQueue, IntArrayIterator

cdef class TradebookIterator:
    cdef IntArrayIterator address_iterator
    cdef IntArrayIterator timestamp_iterator
    cdef FloatArrayIterator trade_price_iterator
    cdef FloatArrayIterator trade_volume_iterator

cdef class Tradebook:
    cdef IntArrayQueue addresses
    cdef IntArrayQueue timestamps
    cdef FloatArrayQueue trade_prices
    cdef FloatArrayQueue trade_volumes

    # Buffer for new trades
    cdef vector[int] timestamps_buffer
    cdef vector[double] trade_prices_buffer
    cdef vector[double] trade_volumes_buffer

    # Getters
    cdef int address_to_index(self, int address)
    cpdef int get_timestamp(self)
    cpdef TradebookIterator get_iterator(self, int from_address = *, int address_timestamp = *)

    # Mutators
    cdef void record_buffer_trades(self)
    cpdef void append_trade(self, int timestamp, double price, double size)
    