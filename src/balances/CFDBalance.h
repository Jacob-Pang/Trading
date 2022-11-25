#pragma once
#include <iostream>
#include "Balance.h"

class CFDBalance: public Balance {
    private:
        HashKey settlement_key;

    public:
        double avg_entry_price;
        CFDBalance(HashKey key, HashKey settlement_key, double size, double entry_price);

        double get_value(double price) const;
        void integrate_into_balances(Balances& balances);
};
