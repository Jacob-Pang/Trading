import numpy as np

from . import PortfolioOptimizerInterface
from .. import Portfolio
from ...price_model import PriceModelBase

class TangentPortfolioOptimizer (PortfolioOptimizerInterface):
    def __init__(self, price_model: PriceModelBase) -> None:
        self.price_model = price_model

    def get_optimized_weights(self, portfolio: Portfolio) -> np.ndarray:
        # Continuous compounded interest
        risk_free_rate = np.exp(self.price_model.get_risk_free_rate() * self.price_model
                .get_time_step_size()) - 1

        port_ret_dist = portfolio.get_ret_dist(self.price_model)
        ret_covar_mat = port_ret_dist.get_covar_mat()
        risk_premium_vect = port_ret_dist.get_expectation_vect() - risk_free_rate

        precision_mat = np.linalg.inv(ret_covar_mat)
        vect_product = np.squeeze(precision_mat @ np.expand_dims(risk_premium_vect, axis=1))

        return vect_product / np.sum(vect_product)

if __name__ == "__main__":
    pass