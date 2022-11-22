import numpy as np

cdef class TradebookIterator:
    def __init__(self, IntArrayIterator address_iterator, IntArrayIterator timestamp_iterator,
        FloatArrayIterator trade_price_iterator, FloatArrayIterator trade_volume_iterator):
        self.address_iterator = address_iterator
        self.timestamp_iterator = timestamp_iterator
        self.trade_price_iterator = trade_price_iterator
        self.trade_volume_iterator = trade_volume_iterator

    def __iter__(self):
        return self
    
    def __next__(self) -> tuple[int, int, float, float]:
        return (self.address_iterator.__next__(), self.timestamp_iterator.__next__(),
                self.trade_price_iterator.__next__(), self.trade_volume_iterator.__next__())

cdef class Tradebook:
    def __init__(self, capacity: int):
        self.addresses = IntArrayQueue(capacity)
        self.timestamps = IntArrayQueue(capacity)
        self.trade_prices = FloatArrayQueue(capacity)
        self.trade_volumes = FloatArrayQueue(capacity)

    # Getters
    cdef int address_to_index(self, int address):
        return (address + self.addresses.get(0)) % self.addresses.get_capacity()

    cpdef int get_timestamp(self):
        # Returns the timestamp for the most recent observation (buffer / record)
        if not self.timestamps_buffer.empty():
            return self.timestamps_buffer[0]

        return self.timestamps.get(-1)

    cpdef TradebookIterator get_iterator(self, int from_address = -1, int address_timestamp = -1):
        if self.timestamps_buffer.size():
            self.record_buffer_trades()

        cdef int start_index = 0

        if from_address > 0: # Validate address using timestamp
            start_index = self.address_to_index(from_address)

            if self.timestamps.get(start_index) != address_timestamp:
                # Invalid address provided
                start_index = 0

        return TradebookIterator(
            self.addresses.get_iterator(start_index),
            self.timestamps.get_iterator(start_index),
            self.trade_prices.get_iterator(start_index),
            self.trade_volumes.get_iterator(start_index)
        )

    # Mutators
    cdef void record_buffer_trades(self):
        # Moves trades in the buffer into the queue record
        cdef int timestamp
        cdef double trade_price
        cdef double trade_size

        while self.timestamps_buffer.size():
            timestamp = self.timestamps_buffer.back()
            trade_price = self.trade_prices_buffer.back()
            trade_size = self.trade_volumes_buffer.back()
            
            self.timestamps_buffer.pop_back()
            self.trade_prices_buffer.pop_back()
            self.trade_volumes_buffer.pop_back()
            
            if self.timestamps.get_size(): # Non-empty record
                assert timestamp >= self.timestamps.get(-1)
                self.addresses.push_back(self.addresses.get(-1) + 1 %
                        self.addresses.get_capacity())
            else:
                self.addresses.push_back(0)
            
            self.timestamps.push_back(timestamp)
            self.trade_prices.push_back(trade_price)
            self.trade_volumes.push_back(trade_size)
            
    cpdef void append_trade(self, int timestamp, double price, double size):
        # Append trades to holding buffer
        if self.timestamps_buffer.size():
            if self.timestamps_buffer[0] < timestamp:
                self.record_buffer_trades()

        self.timestamps_buffer.push_back(timestamp)
        self.trade_prices_buffer.push_back(price)
        self.trade_volumes_buffer.push_back(size)
    

    def __reduce__(self):
        self.record_buffer_trades()

        attrs = { # Extracting the attrs
            "addresses": self.addresses.__reduce__()[2],
            "timestamps": self.timestamps.__reduce__()[2],
            "trade_prices": self.trade_prices.__reduce__()[2],
            "trade_volumes": self.trade_volumes.__reduce__()[2],
        }

        return (self.__class__, (self.addresses.get_capacity(),), attrs)

    def __setstate__(self, attrs):
        self.addresses.__setstate__(attrs.get("addresses"))
        self.timestamps.__setstate__(attrs.get("timestamps"))
        self.trade_prices.__setstate__(attrs.get("trade_prices"))
        self.trade_volumes.__setstate__(attrs.get("trade_volumes"))
