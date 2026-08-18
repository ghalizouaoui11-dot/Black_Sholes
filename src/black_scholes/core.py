
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import erf, exp, isfinite, log, pi, sqrt
from typing import Literal


class OptionType(str, Enum):

    CALL = "call"
    PUT = "put"


OptionTypeLike = OptionType | Literal["call", "put"]


@dataclass(frozen=True, slots=True)
class PricingResult:

    price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float

    def as_dict(self) -> dict[str, float]:
        return {
            "price": self.price,
            "delta": self.delta,
            "gamma": self.gamma,
            "vega": self.vega,
            "theta": self.theta,
            "rho": self.rho,
        }


def _option_type(value: OptionTypeLike) -> OptionType:
    try:
        return OptionType(value.lower()) if isinstance(value, str) else OptionType(value)
    except (AttributeError, ValueError) as exc:
        raise ValueError("option_type must be 'call' or 'put'") from exc


def _validate_inputs(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    risk_free_rate: float,
    dividend_yield: float,
) -> None:
    values = {
        "spot": spot,
        "strike": strike,
        "time_to_expiry": time_to_expiry,
        "volatility": volatility,
        "risk_free_rate": risk_free_rate,
        "dividend_yield": dividend_yield,
    }
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"{name} must be a finite number")
    if spot <= 0:
        raise ValueError("spot must be greater than zero")
    if strike <= 0:
        raise ValueError("strike must be greater than zero")
    if time_to_expiry < 0:
        raise ValueError("time_to_expiry cannot be negative")
    if volatility < 0:
        raise ValueError("volatility cannot be negative")


def _normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def _normal_pdf(value: float) -> float:
    return exp(-0.5 * value * value) / sqrt(2.0 * pi)


def _d1_d2(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    risk_free_rate: float,
    dividend_yield: float,
) -> tuple[float, float]:
    root_time = sqrt(time_to_expiry)
    d1 = (
        log(spot / strike)
        + (risk_free_rate - dividend_yield + 0.5 * volatility**2) * time_to_expiry
    ) / (volatility * root_time)
    return d1, d1 - volatility * root_time


def black_scholes_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    risk_free_rate: float = 0.0,
    option_type: OptionTypeLike = OptionType.CALL,
    dividend_yield: float = 0.0,
) -> float:
    """Return the no-arbitrage value of a European call or put.

    Rates, volatility, dividend yield, and time are decimal/year units: use
    ``0.20`` for 20% volatility and ``30 / 365`` for 30 calendar days.
    """

    _validate_inputs(
        spot, strike, time_to_expiry, volatility, risk_free_rate, dividend_yield
    )
    kind = _option_type(option_type)

    if time_to_expiry == 0:
        payoff = spot - strike if kind is OptionType.CALL else strike - spot
        return max(payoff, 0.0)

    discounted_spot = spot * exp(-dividend_yield * time_to_expiry)
    discounted_strike = strike * exp(-risk_free_rate * time_to_expiry)
    if volatility == 0:
        forward_payoff = (
            discounted_spot - discounted_strike
            if kind is OptionType.CALL
            else discounted_strike - discounted_spot
        )
        return max(forward_payoff, 0.0)

    d1, d2 = _d1_d2(
        spot, strike, time_to_expiry, volatility, risk_free_rate, dividend_yield
    )
    if kind is OptionType.CALL:
        return discounted_spot * _normal_cdf(d1) - discounted_strike * _normal_cdf(d2)
    return discounted_strike * _normal_cdf(-d2) - discounted_spot * _normal_cdf(-d1)


def black_scholes(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    risk_free_rate: float = 0.0,
    option_type: OptionTypeLike = OptionType.CALL,
    dividend_yield: float = 0.0,
) -> PricingResult:
    """Return the price and analytical Greeks for a European option."""

    _validate_inputs(
        spot, strike, time_to_expiry, volatility, risk_free_rate, dividend_yield
    )
    if time_to_expiry == 0 or volatility == 0:
        raise ValueError("Greeks require positive time_to_expiry and volatility")

    kind = _option_type(option_type)
    d1, d2 = _d1_d2(
        spot, strike, time_to_expiry, volatility, risk_free_rate, dividend_yield
    )
    root_time = sqrt(time_to_expiry)
    spot_discount = exp(-dividend_yield * time_to_expiry)
    strike_discount = exp(-risk_free_rate * time_to_expiry)
    density = _normal_pdf(d1)
    price = black_scholes_price(
        spot,
        strike,
        time_to_expiry,
        volatility,
        risk_free_rate,
        kind,
        dividend_yield,
    )
    gamma = spot_discount * density / (spot * volatility * root_time)
    vega = spot * spot_discount * density * root_time
    diffusion_theta = -spot * spot_discount * density * volatility / (2.0 * root_time)

    if kind is OptionType.CALL:
        delta = spot_discount * _normal_cdf(d1)
        theta = (
            diffusion_theta
            - risk_free_rate * strike * strike_discount * _normal_cdf(d2)
            + dividend_yield * spot * spot_discount * _normal_cdf(d1)
        )
        rho = strike * time_to_expiry * strike_discount * _normal_cdf(d2)
    else:
        delta = spot_discount * (_normal_cdf(d1) - 1.0)
        theta = (
            diffusion_theta
            + risk_free_rate * strike * strike_discount * _normal_cdf(-d2)
            - dividend_yield * spot * spot_discount * _normal_cdf(-d1)
        )
        rho = -strike * time_to_expiry * strike_discount * _normal_cdf(-d2)

    return PricingResult(price, delta, gamma, vega, theta, rho)


@dataclass(frozen=True, slots=True)
class BlackScholesModel:
    """Reusable model holding market and contract parameters."""

    spot: float
    strike: float
    time_to_expiry: float
    volatility: float
    risk_free_rate: float = 0.0
    dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        _validate_inputs(
            self.spot,
            self.strike,
            self.time_to_expiry,
            self.volatility,
            self.risk_free_rate,
            self.dividend_yield,
        )

    def price(self, option_type: OptionTypeLike = OptionType.CALL) -> float:
        return black_scholes_price(
            self.spot,
            self.strike,
            self.time_to_expiry,
            self.volatility,
            self.risk_free_rate,
            option_type,
            self.dividend_yield,
        )

    def calculate(self, option_type: OptionTypeLike = OptionType.CALL) -> PricingResult:
        return black_scholes(
            self.spot,
            self.strike,
            self.time_to_expiry,
            self.volatility,
            self.risk_free_rate,
            option_type,
            self.dividend_yield,
        )

