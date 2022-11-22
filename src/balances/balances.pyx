import cython
from cython.operator import dereference, postincrement

cdef class Balances:
    def __init__(self):
        self.hashkey_to_tickers = dict()

    # Getters
    cdef double get_amount(self, long long ticker_hashkey):
        if self.amounts.count(ticker_hashkey):
            return self.amounts.at(ticker_hashkey)
        
        return 0 # Prevent automatic allocation
    
    cpdef double get(self, str ticker):
        return self.get_amount(ticker.__hash__())

    cpdef double get_net_value(self, dict ticker_values):
        cdef double net_value = 0
        cdef unordered_map[long long, double].iterator amounts_iterator = self.amounts.begin()
        
        while (amounts_iterator != self.amounts.end()):
            ticker = self.hashkey_to_tickers.get(dereference(amounts_iterator).first)

            if ticker in ticker_values:
                net_value += ticker_values.get(ticker) * dereference(amounts_iterator).second

            postincrement(amounts_iterator)

        return net_value
    
    # Mutators
    cdef bint add_amount(self, long long ticker_hashkey, double amount):
        if self.amounts.count(ticker_hashkey):
            self.amounts[ticker_hashkey] += amount
            return False
        
        self.amounts[ticker_hashkey] = amount
        return True

    cpdef void add(self, str ticker, double amount):
        cdef long long hashkey = ticker.__hash__()

        if self.add_amount(hashkey, amount):
            self.hashkey_to_tickers[hashkey] = ticker

    cpdef void assimilate(self, Balances other):
        cdef unordered_map[long long, double].iterator amounts_iterator = other.amounts.begin()
        cdef long long hashkey

        while (amounts_iterator != other.amounts.end()):
            hashkey = dereference(amounts_iterator).first

            if self.add_amount(hashkey, dereference(amounts_iterator).second):
                self.hashkey_to_tickers[hashkey] = other.hashkey_to_tickers[hashkey]

            postincrement(amounts_iterator)


    def __repr__(self) -> str:
        amounts_repr = dict()
        cdef unordered_map[long long, double].iterator amounts_iterator = self.amounts.begin()

        while (amounts_iterator != self.amounts.end()):
            amounts_repr[self.hashkey_to_tickers[dereference(amounts_iterator).first]] = dereference(
                    amounts_iterator).second
            
            postincrement(amounts_iterator)

        return amounts_repr.__repr__()

    def __reduce__(self) -> tuple:
        amounts = dict()
        cdef unordered_map[long long, double].iterator amounts_iterator = self.amounts.begin()

        while (amounts_iterator != self.amounts.end()):
            amounts[dereference(amounts_iterator).first] = dereference(amounts_iterator).second
            postincrement(amounts_iterator)

        attrs = {
            "hashkey_to_tickers": self.hashkey_to_tickers,
            "amounts": amounts
        }

        return (self.__class__, tuple(), attrs)

    def __setstate__(self, attrs: dict) -> None:
        self.hashkey_to_tickers = attrs.get("hashkey_to_tickers")
        
        for hashkey, amount in attrs.get("amounts").items():
            self.amounts[hashkey] = amount
