# cython: language = 3
cimport numpy as np

cdef class IndicatorBase:
    cdef str name
    cdef int num_features
    cdef double[:] current_observation
    
    # Getters
    cpdef int get_num_features(self)
    cpdef double get_feature(self, int feature_index)
    cpdef np.ndarray[double, ndim=1] get_observation(self)

    # Mutators
    cpdef void set(self, int feature_index, double feature_value)
    cpdef void update(self)

cdef class FeaturesCompiler:
    cdef list indicators
    cdef int num_features
    cdef double[:] features

    # Getters
    cpdef int get_num_features(self)
    cpdef np.ndarray[double, ndim=1] get(self)
