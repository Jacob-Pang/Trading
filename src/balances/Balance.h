#pragma once
#include <iostream>
#include <unordered_map>

class Balance; // Forward declaration

typedef long long HashKey;
typedef std::unordered_map<HashKey, Balance*> Balances;

class Balance {
    protected:
        HashKey key;

    public:
        double size;
        Balance(HashKey key, double size);
        
        HashKey get_key() const;
        double get_size() const;
        virtual double get_value(double price) const;
        virtual void integrate_into_balances(Balances& balances);
};
