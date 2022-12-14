import time
import numpy as np

cdef class Orderbook:
    # Getters
    cpdef bint empty_bid_orderbook(self):
        return self.bid_prices.size() == 0

    cpdef bint empty_ask_orderbook(self):
        return self.ask_prices.size() == 0

    cpdef tuple get_bid(self, int entry):
        assert entry < self.bid_prices.size()
        return self.bid_prices[entry], self.bid_sizes[entry], self.accum_bid_sizes[entry]

    cpdef tuple get_ask(self, int entry):
        assert entry < self.ask_prices.size()
        return self.ask_prices[entry], self.ask_sizes[entry], self.accum_ask_sizes[entry]

    cpdef tuple get_market_bid(self, double funding_value):
        assert not self.empty_bid_orderbook()
        cdef size_t bid_orderbook_size = self.bid_prices.size()

        cdef double market_bid_size = 0
        cdef double remaining_funding_value = funding_value
        cdef double trade_value

        for entry in range(bid_orderbook_size):
            if remaining_funding_value <= 0: break

            trade_value = min(
                self.bid_prices[entry] * self.bid_sizes[entry],
                remaining_funding_value
            )
            
            market_bid_size += trade_value / self.bid_prices[entry]
            remaining_funding_value -= trade_value

        return (funding_value - remaining_funding_value) / market_bid_size,  market_bid_size
    
    cpdef tuple get_market_ask(self, double funding_value):
        assert not self.empty_ask_orderbook()
        cdef size_t ask_orderbook_size = self.ask_prices.size()

        cdef double market_ask_size = 0
        cdef double remaining_funding_value = funding_value
        cdef double trade_value

        for entry in range(ask_orderbook_size):
            if remaining_funding_value <= 0: break

            trade_value = min(
                self.ask_prices[entry] * self.ask_sizes[entry],
                remaining_funding_value
            )
            
            market_ask_size += trade_value / self.ask_prices[entry]
            remaining_funding_value -= trade_value

        return (funding_value - remaining_funding_value) / market_ask_size, market_ask_size

    cpdef double get_market_bid_price(self, double order_size):
        assert not self.empty_bid_orderbook()
        cdef size_t bid_orderbook_size = self.bid_prices.size()

        if order_size > self.accum_bid_sizes[bid_orderbook_size - 1]:
            return self.bid_prices[bid_orderbook_size - 1]

        cdef double trade_value = 0
        cdef double remaining_size = order_size
        cdef double trade_size

        for entry in range(bid_orderbook_size):
            if remaining_size <= 0: break

            trade_size = min(self.bid_sizes[entry], remaining_size)
            trade_value += self.bid_prices[entry] * trade_size
            remaining_size -= trade_size

        return trade_value / order_size

    cpdef double get_market_ask_price(self, double order_size):
        assert not self.empty_ask_orderbook()
        cdef size_t ask_orderbook_size = self.ask_prices.size()

        if order_size > self.accum_ask_sizes[ask_orderbook_size - 1]:
            return self.ask_prices[ask_orderbook_size - 1]

        cdef double trade_value = 0
        cdef double remaining_size = order_size
        cdef double trade_size

        for entry in range(ask_orderbook_size):
            if remaining_size <= 0: break

            trade_size = min(self.ask_sizes[entry], remaining_size)
            trade_value += self.ask_prices[entry] * trade_size
            remaining_size -= trade_size

        return trade_value / order_size

    # Mutators
    cpdef void reset(self):
        self.bid_prices.clear()
        self.bid_sizes.clear()
        self.accum_bid_sizes.clear()
        self.ask_prices.clear()
        self.ask_sizes.clear()
        self.accum_ask_sizes.clear()
        self.timestamp = int(time.time())
    
    cpdef void append_bid(self, double bid_price, double bid_size) except +:
        cdef size_t bid_orderbook_size = self.bid_prices.size()
        
        if bid_orderbook_size == 0:
            self.accum_bid_sizes.push_back(bid_size)
        else: # Ensure descending order
            assert bid_price < self.bid_prices[bid_orderbook_size - 1]
            self.accum_bid_sizes.push_back(self.accum_bid_sizes[bid_orderbook_size - 1] + bid_size)
        
        self.bid_prices.push_back(bid_price)
        self.bid_sizes.push_back(bid_size)

    cpdef void append_ask(self, double ask_price, double ask_size) except +:
        cdef size_t ask_orderbook_size = self.ask_prices.size()

        if ask_orderbook_size == 0:
            self.accum_ask_sizes.push_back(ask_size)
        else: # Ensure ascending order
            assert ask_price > self.ask_prices[ask_orderbook_size - 1]
            self.accum_ask_sizes.push_back(self.accum_ask_sizes[ask_orderbook_size - 1] + ask_size)
        
        self.ask_prices.push_back(ask_price)
        self.ask_sizes.push_back(ask_size)
