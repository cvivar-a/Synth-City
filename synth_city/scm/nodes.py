"""
Structural equations for the Synth City people-level DAG.

Each function has the signature:

    f(rng: np.random.Generator, n: int, **parents) -> np.ndarray

`parents` contains one keyword arg per parent node (including policy
nodes, e.g. `min_wage`), each a length-n numpy array. Every function
returns a length-n numpy array: the sampled values for that node
across all n people.

Keeping every equation vectorized (no per-person python loop) is what
lets `SynthCity.sample()` scale to large populations.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Exogenous / latent nodes (no parents)
# ---------------------------------------------------------------------------

def f_ability(rng: np.random.Generator, n: int, **_) -> np.ndarray:
    """Latent cognitive/skill trait."""
    return rng.normal(0, 1, n)


def f_risk_tolerance(rng: np.random.Generator, n: int, **_) -> np.ndarray:
    """Latent trait affecting schooling-vs-work and consumption choices."""
    return rng.normal(0, 1, n)


def f_health_endowment(rng: np.random.Generator, n: int, **_) -> np.ndarray:
    """Latent baseline health, independent of behavior."""
    return rng.normal(0, 1, n)


def f_parental_ses(rng: np.random.Generator, n: int, **_) -> np.ndarray:
    """Latent socioeconomic background of the person's family of origin."""
    return rng.normal(0, 1, n)


def f_age(rng: np.random.Generator, n: int, **_) -> np.ndarray:
    return rng.uniform(18, 75, n)


# ---------------------------------------------------------------------------
# Endogenous nodes
# ---------------------------------------------------------------------------

def f_education(
    rng: np.random.Generator,
    n: int,
    ability: np.ndarray,
    parental_ses: np.ndarray,
    risk_tolerance: np.ndarray,
    age: np.ndarray,
    **_,
) -> np.ndarray:
    """Years of education, in [6, 22]."""
    years = (
        10
        + 2.5 * ability
        + 1.8 * parental_ses
        - 0.4 * risk_tolerance
        + 0.02 * (age - 40)
        + rng.normal(0, 1.2, n)
    )
    return np.clip(years, 6, 22)


def f_social_network_position(
    rng: np.random.Generator,
    n: int,
    parental_ses: np.ndarray,
    education: np.ndarray,
    **_,
) -> np.ndarray:
    """Standardized centrality-like score; homophilous on SES and education."""
    return 0.6 * parental_ses + 0.5 * (education - 10) / 5 + rng.normal(0, 1, n)


def f_income(
    rng: np.random.Generator,
    n: int,
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
    naive regression biased and gives Stage 2 estimators something to
    correct for.
    """
    base = (
        15_000
        + 3_200 * education
        + 250 * (age - 18)
        - 0.3 * (age - 45) ** 2
        + 1_800 * social_network_position
        + 2_500 * ability
        + rng.normal(0, 6_000, n)
    )
    after_tax = base * (1 - tax_rate)
    annual_floor = min_wage * 2_080  # ~40 hrs/week * 52 weeks
    return np.maximum(after_tax, annual_floor)


def f_mobility_access(
    rng: np.random.Generator,
    n: int,
    income: np.ndarray,
    health_endowment: np.ndarray,
    transit_subsidy: np.ndarray,
    **_,
) -> np.ndarray:
    """Standardized mobility/access score (car ownership, transit access, ...)."""
    return (
        0.00002 * income
        + 0.3 * health_endowment
        + 0.05 * transit_subsidy
        + rng.normal(0, 0.5, n)
    )


def f_health(
    rng: np.random.Generator,
    n: int,
    health_endowment: np.ndarray,
    income: np.ndarray,
    mobility_access: np.ndarray,
    age: np.ndarray,
    **_,
) -> np.ndarray:
    """Standardized health score."""
    return (
        5 * health_endowment
        + 0.00003 * income
        + 0.4 * mobility_access
        - 0.01 * np.clip(age - 30, 0, None)
        + rng.normal(0, 1, n)
    )


def f_preferences(
    rng: np.random.Generator,
    n: int,
    income: np.ndarray,
    social_network_position: np.ndarray,
    **_,
) -> np.ndarray:
    """Standardized consumption/risk preference score -- feeds Stage 3 behavior models."""
    return 0.00001 * income + 0.3 * social_network_position + rng.normal(0, 1, n)


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

# Policy / intervention nodes and their default values.
POLICY_NODES: dict[str, float] = {
    "min_wage": 7.25,
    "tax_rate": 0.20,
    "transit_subsidy": 0.0,
}
