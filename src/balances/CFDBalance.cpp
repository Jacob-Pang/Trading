#include "CFDBalance.h"

CFDBalance::CFDBalance(HashKey key, HashKey settlement_key, double size, double entry_price):
    Balance::Balance(key, size) {
    this->settlement_key = settlement_key;
    this->avg_entry_price = entry_price;
};

double CFDBalance::get_value(double price) const {
    return this->size * price;
};

void CFDBalance::integrate_into_balances(Balances& balances) {
    if (balances.count(this->key) == 0) {
        Balance* balance = new CFDBalance(this->key, this->settlement_key, this->size,
                this->avg_entry_price);
        
        balances[this->key] = balance;
        return;
    }

    CFDBalance* balance = dynamic_cast<CFDBalance*>(balances[this->key]);
    
    if (this->size > 0 == balance->size > 0) {
        balance->avg_entry_price = (this->avg_entry_price * this->size +
                balance->avg_entry_price * balance->size) /
                (this->size + balance->size);
        
        balance->size += this->size;
        balances[this->key] = (Balance*) balance;
        return;
    }

    double long_price, short_price;
    double long_size, short_size, settlement_size;

    if (this->size > 0) {
        long_price = this->avg_entry_price;
        long_size = this->size;
        short_price = balance->avg_entry_price;
        short_size = -balance->size;
    } else {
        long_price = balance->avg_entry_price;
        long_size = balance->size;
        short_price = this->avg_entry_price;
        short_size = -this->size;
    }
    
    if (long_size > short_size) {
        settlement_size = short_size * (short_price - long_price);
        balance->avg_entry_price = long_price;
    } else { // short_size >= long_size
        settlement_size = long_size * (short_price - long_price);
        balance->avg_entry_price = short_price;
    }

    balance->size = long_size - short_size;
    Balance* settlement = new Balance(this->settlement_key, settlement_size);
    settlement->integrate_into_balances(balances);
    
    if (balance->size) {
        balances[this->key] = (Balance*) balance;
    } else {
        balances.erase(this->key);
    }
};
