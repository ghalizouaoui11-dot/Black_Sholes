import math
import unittest

from black_scholes import BlackScholesModel, black_scholes, black_scholes_price


class PricingTests(unittest.TestCase):
    def test_textbook_call_and_put_values(self):
        call = black_scholes_price(100, 100, 1, 0.2, 0.05, "call")
        put = black_scholes_price(100, 100, 1, 0.2, 0.05, "put")
        self.assertAlmostEqual(call, 10.450583572, places=8)
        self.assertAlmostEqual(put, 5.573526022, places=8)

    def test_put_call_parity_with_dividends(self):
        call = black_scholes_price(110, 100, 0.75, 0.3, 0.04, "call", 0.015)
        put = black_scholes_price(110, 100, 0.75, 0.3, 0.04, "put", 0.015)
        parity = 110 * math.exp(-0.015 * 0.75) - 100 * math.exp(-0.04 * 0.75)
        self.assertAlmostEqual(call - put, parity, places=10)

    def test_expiry_and_zero_volatility_boundaries(self):
        self.assertEqual(black_scholes_price(120, 100, 0, 0.2), 20)
        expected = max(120 - 100 * math.exp(-0.05), 0)
        self.assertAlmostEqual(black_scholes_price(120, 100, 1, 0, 0.05), expected)

    def test_model_and_functional_api_agree(self):
        model = BlackScholesModel(100, 95, 0.5, 0.25, 0.03, 0.01)
        self.assertEqual(model.price("put"), black_scholes(100, 95, 0.5, 0.25, 0.03, "put", 0.01).price)
        result = model.calculate("call")
        self.assertGreater(result.gamma, 0)
        self.assertGreater(result.vega, 0)
        self.assertEqual(set(result.as_dict()), {"price", "delta", "gamma", "vega", "theta", "rho"})

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            black_scholes_price(-1, 100, 1, 0.2)
        with self.assertRaises(ValueError):
            black_scholes_price(100, 100, 1, 0.2, option_type="straddle")


if __name__ == "__main__":
    unittest.main()

