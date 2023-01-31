# cython: language_level = 3
# distutils: language = c++
cimport numpy as np

from pyutils.array_queue.float_array_queue cimport ContiguousFloatArrayQueue
from ..tradebook.tradebook cimport Tradebook
from ..tradebook.tradebook cimport TradebookIterator

cdef class CandleBuffer:
    cdef ContiguousFloatArrayQueue open_buffer
    cdef ContiguousFloatArrayQueue high_buffer
    cdef ContiguousFloatArrayQueue low_buffer
    cdef ContiguousFloatArrayQueue close_buffer
    cdef ContiguousFloatArrayQueue volume_buffer
    cdef int frame_resolution
    cdef int time_frame
    cdef int tradebook_address
    cdef int tradebook_timestamp

    # Getters
    cpdef int get_size(self)
    cpdef int get_capacity(self)
    cpdef int get_time_frame(self)
    cpdef np.ndarray[double, ndim=1] get_open_data(self, int frames = *)
    cpdef np.ndarray[double, ndim=1] get_high_data(self, int frames = *)
    cpdef np.ndarray[double, ndim=1] get_low_data(self, int frames = *)
    cpdef np.ndarray[double, ndim=1] get_close_data(self, int frames = *)
    cpdef np.ndarray[double, ndim=1] get_volume_data(self, int frames = *)
    cpdef tuple get_data(self, int frames = *)

    # Mutators
    cpdef void reset(self)
    cpdef void set_time_frame(self, int timestamp)
    cpdef void update(self, int timestamp, double curr_price, Tradebook tradebook)
    cpdef void set_data(self, int timestamp, np.ndarray[double, ndim=1] open_values,
        np.ndarray[double, ndim=1] high_values, np.ndarray[double, ndim=1] low_values,
        np.ndarray[double, ndim=1] close_values, np.ndarray[double, ndim=1] volumes)

if __name__ == "__main__":
    pass