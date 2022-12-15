
cdef class CostEngine:
    def __init__(self, flat_cost: float = 0, min_cost: float = 0, percent_cost_rate: float = 0):
        self.flat_cost = flat_cost
        self.min_cost = min_cost
        self.percent_cost_rate = percent_cost_rate

        self.filled_size = 0
        self.filled_cost = 0

    cpdef double get_flat_cost(self):
        return self.flat_cost
    
    cpdef double get_min_cost(self):
        return self.min_cost
    
    cpdef double get_percent_cost_rate(self):
        return self.percent_cost_rate

    cpdef double get_filled_size(self):
        return self.filled_size
    
    cpdef double get_filled_cost(self):
        return self.filled_cost

    cpdef double get_fill_cost(self, double fill_size):
        cdef double running_cost = self.flat_cost + self.percent_cost_rate * abs(self.filled_size + fill_size)

        if running_cost < self.min_cost:
            return min(abs(fill_size), self.min_cost - self.filled_cost)

        return max(running_cost - self.filled_cost, 0)

    cpdef double fill_order(self, double fill_size):
        cdef double fill_cost = self.get_fill_cost(fill_size)

        self.filled_size += fill_size
        self.filled_cost += fill_cost

        return fill_cost
