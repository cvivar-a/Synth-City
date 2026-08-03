"""
Structural equations for the Synth City people-level DAG.

Every coefficient, clip bound, and noise scale used here is read from a
`params` object defined in config.py -- there are no bare numeric literals
in the equations below. To recalibrate the model, edit config.py; these
functions should never need to change just because a number changes.

Each function has the signature:

    f(rng: np.random.Generator, n: int, params: <SomeParams>, **parents) -> np.ndarray

`parents` contains one keyword arg per parent node (including policy nodes,
e.g. `min_wage`), each a length-n numpy array. Every function returns a
length-n numpy array: the sampled values for that node across all n people.

Keeping every equation vectorized (no per-person python loop) is what lets
`SynthCity.sample()` scale to large populations.
"""

from __future__ import annotations

import numpy as np

from .config import (
    AgeParams,
    EducationParams,
    HealthParams,
    IncomeParams,
    LatentParams,
    MobilityParams,
    PreferencesParams,
    SocialNetworkParams,
)


# ---------------------------------------------------------------------------
# Exogenous / latent nodes (no parents)
# ---------------------------------------------------------------------------

def f_ability(rng: np.random.Generator, n: int, params: LatentParams, **_) -> np.ndarray:
    """Latent cognitive/skill trait."""
    return rng.normal(params.mean, params.std, n)


def f_risk_tolerance(rng: np.random.Generator, n: int, params: LatentParams, **_) -> np.ndarray:
    """Latent trait affecting schooling-vs-work and consumption choices."""
    return rng.normal(params.mean, params.std, n)


def f_health_endowment(rng: np.random.Generator, n: int, params: LatentParams, **_) -> np.ndarray:
    """Latent baseline health, independent of behavior."""
    return rng.normal(params.mean, params.std, n)


def f_parental_ses(rng: np.random.Generator, n: int, params: LatentParams, **_) -> np.ndarray:
    """Latent socioeconomic background of the person's family of origin."""
    return rng.normal(params.mean, params.std, n)


def f_age(rng: np.random.Generator, n: int, params: AgeParams, **_) -> np.ndarray:
    """
    A rough population pyramid instead of a flat draw: a mixture of a
    "younger" and an "older" normal component, mixed by params.older_share.
    """
    is_older = rng.random(n) < params.older_share
    younger = rng.normal(params.younger_mean, params.younger_std, n)
    older = rng.normal(params.older_mean, params.older_std, n)
    age = np.where(is_older, older, younger)
    return np.clip(age, params.min_age, params.max_age)


# ---------------------------------------------------------------------------
# Endogenous nodes
# ---------------------------------------------------------------------------

def f_education(
    rng: np.random.Generator,
    n: int,
    params: EducationParams,
    ability: np.ndarray,
    parental_ses: np.ndarray,
    risk_tolerance: np.ndarray,
    age: np.ndarray,
    **_,
) -> np.ndarray:
    """Years of education, clipped to [params.min_years, params.max_years]."""
    years = (
        params.intercept_years
        + params.ability_coef * ability
        + params.parental_ses_coef * parental_ses
        + params.risk_tolerance_coef * risk_tolerance
        + params.age_coef * (age - params.age_reference)
        + rng.normal(0, params.noise_std, n)
    )
    return np.clip(years, params.min_years, params.max_years)


def f_social_network_position(
    rng: np.random.Generator,
    n: int,
    params: SocialNetworkParams,
    parental_ses: np.ndarray,
    education: np.ndarray,
    **_,
) -> np.ndarray:
    """Standardized centrality-like score; homophilous on SES and education."""
    return (
        params.parental_ses_coef * parental_ses
        + params.education_coef * (education - params.education_reference) / params.education_scale
        + rng.normal(0, params.noise_std, n)
    )


def f_income(
    rng: np.random.Generator,
    n: int,
    params: IncomeParams,
    education: np.ndarray,
    age: np.ndarray,
    social_network_position: np.ndarray,
    ability: np.ndarray,
    min_wage: np.ndarray,
    tax_rate: np.ndarray,
    **_,
) -> np.ndarray:
    """
    Annual after-tax income, floored at an annualized minimum wage.

    NOTE: `ability` affects income directly here, not only through
    `education` -- this is the deliberate hidden confounder that makes
    naive regression biased. See IncomeParams docstring in config.py.
    """
    base = (
        params.intercept
        + params.education_coef * education
        + params.age_coef * (age - params.age_min_reference)
        - params.age_penalty_coef * (age - params.age_penalty_reference) ** 2
        + params.social_network_coef * social_network_position
        + params.ability_coef * ability
    )
    # multiplicative lognormal noise -> right-skewed income, not just
    # skewed by the wage floor truncating the left tail
    noise_multiplier = rng.lognormal(mean=0.0, sigma=params.noise_lognormal_sigma, size=n)
    base = base * noise_multiplier

    after_tax = base * (1 - tax_rate)
    annual_floor = min_wage * params.hours_per_year
    return np.maximum(after_tax, annual_floor)


def f_mobility_access(
    rng: np.random.Generator,
    n: int,
    params: MobilityParams,
    income: np.ndarray,
    health_endowment: np.ndarray,
    transit_subsidy: np.ndarray,
    **_,
) -> np.ndarray:
    """Standardized mobility/access score (car ownership, transit access, ...)."""
    return (
        params.income_coef * income
        + params.health_endowment_coef * health_endowment
        + params.transit_subsidy_coef * transit_subsidy
        + rng.normal(0, params.noise_std, n)
    )


def f_health(
    rng: np.random.Generator,
    n: int,
    params: HealthParams,
    health_endowment: np.ndarray,
    income: np.ndarray,
    mobility_access: np.ndarray,
    age: np.ndarray,
    **_,
) -> np.ndarray:
    """Standardized health score."""
    return (
        params.health_endowment_coef * health_endowment
        + params.income_coef * income
        + params.mobility_access_coef * mobility_access
        - params.age_penalty_coef * np.clip(age - params.age_penalty_reference, 0, None)
        + rng.normal(0, params.noise_std, n)
    )


def f_preferences(
    rng: np.random.Generator,
    n: int,
    params: PreferencesParams,
    income: np.ndarray,
    social_network_position: np.ndarray,
    **_,
) -> np.ndarray:
    """Standardized consumption/risk preference score -- feeds Stage 3 behavior models."""
    return (
        params.income_coef * income
        + params.social_network_coef * social_network_position
        + rng.normal(0, params.noise_std, n)
    )


# ---------------------------------------------------------------------------
# Registry: node name -> (function, [parent node names])
# Parent lists may include policy node names (e.g. "min_wage") -- those are
# resolved from SynthCity.policy rather than sampled.
# ---------------------------------------------------------------------------

NODE_SPECS: dict[str, tuple] = {
    "ability": (f_ability, []),
    "risk_tolerance": (f_risk_tolerance, []),
    "health_endowment": (f_health_endowment, []),
    "parental_ses": (f_parental_ses, []),
    "age": (f_age, []),
    "education": (f_education, ["ability", "parental_ses", "risk_tolerance", "age"]),
    "social_network_position": (f_social_network_position, ["parental_ses", "education"]),
    "income": (
        f_income,
        ["education", "age", "social_network_position", "ability", "min_wage", "tax_rate"],
    ),
    "mobility_access": (f_mobility_access, ["income", "health_endowment", "transit_subsidy"]),
    "health": (f_health, ["health_endowment", "income", "mobility_access", "age"]),
    "preferences": (f_preferences, ["income", "social_network_position"]),
}