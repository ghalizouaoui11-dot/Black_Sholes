import unittest

from black_scholes import plot_price_curves, plot_price_heatmap, price_heatmap_data


class HeatmapTests(unittest.TestCase):
    def test_data_shape_and_price_direction(self):
        data = price_heatmap_data(
            [80, 100, 120], [0.1, 0.2], strike=100, time_to_expiry=1, risk_free_rate=0.05
        )
        self.assertEqual(len(data.prices), 2)
        self.assertEqual(len(data.prices[0]), 3)
        self.assertLess(data.prices[0][0], data.prices[0][2])
        self.assertLess(data.prices[0][1], data.prices[1][1])

    def test_seaborn_plots_are_returned_without_file_output(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure, axes, _ = plot_price_heatmap(
            [80, 100, 120], [0.1, 0.2, 0.3], strike=100, time_to_expiry=1, show=False
        )
        self.assertEqual(len(axes.collections), 1)
        curves_figure, curves_axes, _ = plot_price_curves(
            [80, 100, 120], [0.1, 0.2, 0.3], strike=100, time_to_expiry=1, show=False
        )
        self.assertGreaterEqual(len(curves_axes.lines), 4)
        plt.close(figure)
        plt.close(curves_figure)


if __name__ == "__main__":
    unittest.main()
