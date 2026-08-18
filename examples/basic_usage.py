from black_scholes import BlackScholesModel, plot_price_curves, plot_price_heatmap

model = BlackScholesModel(
    spot=100,
    strike=100,
    time_to_expiry=1,
    volatility=0.20,
    risk_free_rate=0.05,
)
print(model.calculate("call").as_dict())

plot_price_heatmap(
    spot_prices=range(70, 131, 10),
    volatilities=[0.10, 0.20, 0.30, 0.40, 0.50],
    strike=model.strike,
    time_to_expiry=model.time_to_expiry,
    risk_free_rate=model.risk_free_rate,
    option_type="call",
    show=False,
)
plot_price_curves(
    spot_prices=range(70, 131, 10),
    volatilities=[0.10, 0.20, 0.30, 0.40, 0.50],
    strike=model.strike,
    time_to_expiry=model.time_to_expiry,
    risk_free_rate=model.risk_free_rate,
    option_type="call",
)

