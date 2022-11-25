#include "Balance.h"

Balance::Balance(HashKey key, double size) {
    this->key = key;
    this->size = size;
};

HashKey Balance::get_key() const {
    return this->key;
};

double Balance::get_size() const {
    return this->size;
};

double Balance::get_value(double price) const {
    return this->size * price;
};

void Balance::integrate_into_balances(Balances& balances) {
    if (balances.count(this->key)) {
        balances[this->key]->size += this->size;
    } else {
        Balance* balance = new Balance(this->key, this->size);
        balances[this->key] = balance;
    }
};
