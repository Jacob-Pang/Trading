import time
import numpy as np

cdef class CandleBuffer:
    def __init__(self, frame_resolution: int, array_capacity: int, container_capacity: int = None):
        self.open_buffer = ContiguousFloatArrayQueue(array_capacity, container_capacity)
        self.high_buffer = ContiguousFloatArrayQueue(array_capacity, container_capacity)
        self.low_buffer = ContiguousFloatArrayQueue(array_capacity, container_capacity)
        self.close_buffer = ContiguousFloatArrayQueue(array_capacity, container_capacity)
        self.volume_buffer = ContiguousFloatArrayQueue(array_capacity, container_capacity)

        self.frame_resolution = frame_resolution
        self.reset()

    # Getters
    cpdef int get_size(self):
        return self.open_buffer.get_size()
    
    cpdef int get_capacity(self):
        return self.open_buffer.get_capacity()

    cpdef int get_time_frame(self):
        return self.time_frame
    
    cpdef np.ndarray[double, ndim=1] get_open_data(self, int frames = 0):
        return self.open_buffer.get_data(start_index=(-frames))
    
    cpdef np.ndarray[double, ndim=1] get_high_data(self, int frames = 0):
        return self.high_buffer.get_data(start_index=(-frames))

    cpdef np.ndarray[double, ndim=1] get_low_data(self, int frames = 0):
        return self.low_buffer.get_data(start_index=(-frames))

    cpdef np.ndarray[double, ndim=1] get_close_data(self, int frames = 0):
        return self.close_buffer.get_data(start_index=(-frames))

    cpdef np.ndarray[double, ndim=1] get_volume_data(self, int frames = 0):
        return self.volume_buffer.get_data(start_index=(-frames))

    cpdef tuple get_data(self, int frames = 0):
        return (
            self.get_open_data(frames),
            self.get_high_data(frames),
            self.get_low_data(frames),
            self.get_close_data(frames),
            self.get_volume_data(frames)
        )

    # Mutators
    cpdef void reset(self):
        self.open_buffer.clear()
        self.high_buffer.clear()
        self.low_buffer.clear()
        self.close_buffer.clear()
        self.volume_buffer.clear()

        self.set_time_frame(time.time())
        self.tradebook_address = -1
        self.tradebook_timestamp = -1

    cpdef void set_time_frame(self, int timestamp):
        self.time_frame = timestamp - (timestamp % self.frame_resolution) + self.frame_resolution

    cpdef void update(self, int timestamp, double curr_price, Tradebook tradebook):
        cdef TradebookIterator tradebook_iterator = tradebook.get_iterator(self.tradebook_address,
                self.tradebook_timestamp)
        
        cdef int tradebook_address
        cdef int tradebook_timestamp
        cdef double trade_price
        cdef double trade_size
        cdef double open_price
        cdef bint transitioned

        if not self.get_size(): # First time frame
            self.set_time_frame(timestamp)
            self.open_buffer.push_back(curr_price)
            self.high_buffer.push_back(curr_price)
            self.low_buffer.push_back(curr_price)
            self.close_buffer.push_back(curr_price)
            self.volume_buffer.push_back(0)

            self.tradebook_timestamp = self.time_frame - self.frame_resolution

        elif timestamp > self.time_frame:
            # Transition to next time frame
            open_price = self.close_buffer.get(-1)
            transitioned = False

            self.open_buffer.push_back(open_price)
            self.high_buffer.push_back(max(curr_price, open_price))
            self.low_buffer.push_back(min(curr_price, open_price))
            self.close_buffer.push_back(curr_price)
            
            for tradebook_address, tradebook_timestamp, trade_price, trade_size in tradebook_iterator:
                if (tradebook_address == self.tradebook_address) or (tradebook_timestamp <
                    self.tradebook_timestamp):
                    continue
                
                if tradebook_timestamp >= self.time_frame:
                    if transitioned:
                        break
                    
                    self.time_frame = self.time_frame + self.frame_resolution
                    self.volume_buffer.push_back(0)
                    transitioned = True

                self.volume_buffer.set(-1, self.volume_buffer.get(-1) + trade_price * trade_size)
                self.tradebook_address = tradebook_address
                self.tradebook_timestamp = tradebook_timestamp
            
            if not transitioned:
                self.time_frame = self.time_frame + self.frame_resolution
                self.volume_buffer.push_back(0)

            return

        else: # Within same time frame
            if curr_price > self.high_buffer.get(-1):
                self.high_buffer.set(-1, curr_price)
            elif curr_price < self.low_buffer.get(-1):
                self.low_buffer.set(-1, curr_price)

            self.close_buffer.set(-1, curr_price)

        for tradebook_address, tradebook_timestamp, trade_price, trade_size in tradebook_iterator:
            if (tradebook_address == self.tradebook_address) or (tradebook_timestamp <
                self.tradebook_timestamp):
                continue
            
            if tradebook_timestamp >= self.time_frame:
                break

            self.volume_buffer.set(-1, self.volume_buffer.get(-1) + trade_price * trade_size)
            self.tradebook_address = tradebook_address
            self.tradebook_timestamp = tradebook_timestamp

    cpdef void set_data(self, int timestamp, np.ndarray[double, ndim=1] open_values,
        np.ndarray[double, ndim=1] high_values, np.ndarray[double, ndim=1] low_values,
        np.ndarray[double, ndim=1] close_values, np.ndarray[double, ndim=1] volumes):

        cdef int size = open_values.shape[0]

        for index in range(size):
            self.open_buffer.push_back(open_values[index])
            self.high_buffer.push_back(high_values[index])
            self.low_buffer.push_back(low_values[index])
            self.close_buffer.push_back(close_values[index])
            self.volume_buffer.push_back(volumes[index])
        
        self.set_time_frame(timestamp)

    
    def __reduce__(self):
        attrs = {
            "open_buffer": self.open_buffer.__reduce__()[2],
            "high_buffer": self.high_buffer.__reduce__()[2],
            "low_buffer": self.low_buffer.__reduce__()[2],
            "close_buffer": self.close_buffer.__reduce__()[2],
            "volume_buffer": self.volume_buffer.__reduce__()[2],
            "time_frame": self.time_frame,
            "tradebook_address": self.tradebook_address,
            "tradebook_timestamp": self.tradebook_timestamp
        }

        return (self.__class__, (self.frame_resolution, self.open_buffer.get_capacity(),
                self.open_buffer.get_container_capacity()), attrs)

    def __setstate__(self, attrs):
        self.open_buffer.__setstate__(attrs.get("open_buffer"))
        self.high_buffer.__setstate__(attrs.get("high_buffer"))
        self.low_buffer.__setstate__(attrs.get("low_buffer"))
        self.close_buffer.__setstate__(attrs.get("close_buffer"))
        self.volume_buffer.__setstate__(attrs.get("volume_buffer"))

        self.time_frame = attrs.get("time_frame")
        self.tradebook_address = attrs.get("tradebook_address")
        self.tradebook_timestamp = attrs.get("tradebook_timestamp")
