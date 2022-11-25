import cython
from cython.operator import dereference, postincrement

cdef class Balances:
    def __init__(self):
        self.keys_to_tickers = dict()

    # Getters
    cpdef double get_size(self, str ticker):
        cdef long long key = ticker.__hash__()

        if self.balances.count(ticker.__hash__()) > 0:
            return self.balances[ticker.__hash__()].get_size()

        return 0

    cpdef double get_value(self, str ticker, double price):
        cdef long long key = ticker.__hash__()

        if self.balances.count(ticker.__hash__()) > 0:
            return self.balances[ticker.__hash__()].get_value(price)

        return 0

    # Mutators
    cpdef void add_balance(self, str ticker, double size):
        cdef long long key = ticker.__hash__()
        cdef Balance* balance = new Balance(key, size)

        if not self.balances.count(key):
            self.keys_to_tickers[key] = ticker
        
        balance.integrate_into_balances(self.balances)

    cpdef void add_cfd_balance(self, str ticker, str settlement_ticker, double size, double entry_price):
        cdef long long key = ticker.__hash__()
        cdef Balance* balance = new CFDBalance(key, settlement_ticker.__hash__(), size, entry_price)

        if not self.balances.count(key):
            self.keys_to_tickers[key] = ticker
        
        balance.integrate_into_balances(self.balances)
        self.add_balance(settlement_ticker, 0) # Create balance for settlement currency.

    cpdef void assimilate(self, Balances other):
        cdef unordered_map[long long, Balance*].iterator balance_iterator = other.balances.begin()
        cdef long long key

        while (balance_iterator != other.balances.end()):
            key = dereference(balance_iterator).first

            if not self.balances.count(key):
                self.keys_to_tickers[key] = other.keys_to_tickers[key]
            
            dereference(balance_iterator).second.integrate_into_balances(self.balances)
            postincrement(balance_iterator)


    def __repr__(self) -> str:
        balances_repr = dict()
        cdef unordered_map[long long, Balance*].iterator balance_iterator = self.balances.begin()

        while (balance_iterator != self.balances.end()):
            balances_repr[self.keys_to_tickers[dereference(balance_iterator).first]] = dereference(
                    balance_iterator).second.get_size()
            
            postincrement(balance_iterator)

        return balances_repr.__repr__()

    def __reduce__(self) -> tuple:
        # Does not save balances
        return (self.__class__, tuple(),)

    def __dealloc__(self):
        cdef unordered_map[long long, Balance*].iterator balance_iterator = self.balances.begin()

        while (balance_iterator != self.balances.end()):
            del dereference(balance_iterator).second
            balance_iterator = self.balances.erase(balance_iterator)
