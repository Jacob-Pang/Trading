
cdef class CostEngine:
    cdef double flat_cost
    cdef double min_cost
    cdef double variable_cost_rate
    cdef double filled_size
    cdef double filled_cost

    # Accessors
    cpdef double get_flat_cost(self)
    cpdef double get_min_cost(self)
    cpdef double get_variable_cost_rate(self)
    cpdef double get_filled_size(self)
    cpdef double get_filled_cost(self)

    cpdef double get_fill_cost(self, double fill_size)

    # Mutators
    cpdef double fill_order(self, double fill_size)
