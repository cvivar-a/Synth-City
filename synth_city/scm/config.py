"""
Every tunable number in the Synth City structural causal model, in one place.

nodes.py should contain no bare numeric literals in its structural equations --
every coefficient, clip bound, and noise scale is a named field here instead.
To recalibrate the model, edit this file; you should never need to touch a
formula in nodes.py just to change a number.

Each dataclass groups the parameters for one node's structural equation.
All are frozen (immutable) so a given SCMParams instance can't be mutated
accidentally mid-simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LatentParams:
    """Shared shape for the four standard-normal latent traits."""
    mean: float = 0.0
    std: float = 1.0


@dataclass(frozen=True)
class AgeParams:
    """
    Age is a mixture of two normals (a population-pyramid approximation):
    a "younger" component and an "older" component, mixed by older_share.
    """
    older_share: float = 0.3
    younger_mean: float = 32.0
    younger_std: float = 8.0
    older_mean: float = 58.0
    older_std: float = 10.0
    min_age: float = 18.0
    max_age: float = 100.0


@dataclass(frozen=True)
class EducationParams:
    intercept_years: float = 10.0
    ability_coef: float = 2.5
    parental_ses_coef: float = 1.8
    risk_tolerance_coef: float = -0.4
    age_coef: float = 0.02
    age_reference: float = 40.0          # age is centered on this before applying age_coef
    noise_std: float = 1.2
    min_years: float = 6.0
    max_years: float = 22.0


@dataclass(frozen=True)
class SocialNetworkParams:
    parental_ses_coef: float = 0.6
    education_coef: float = 0.5
    education_reference: float = 10.0     # education is centered on this...
    education_scale: float = 5.0          # ...then divided by this before applying education_coef
    noise_std: float = 1.0


@dataclass(frozen=True)
class IncomeParams:
    """
    NOTE: ability_coef is a deliberate hidden confounder -- ability affects
    income directly here, not only through education. This is what makes
    naive regression biased and gives Stage 2 causal estimators something
    real to correct for. Don't remove it when recalibrating.
    """
    intercept: float = 15_000.0
    education_coef: float = 3_200.0
    age_coef: float = 250.0
    age_min_reference: float = 18.0       # age contributes (age - age_min_reference) * age_coef
    age_penalty_coef: float = 0.3
    age_penalty_reference: float = 45.0   # quadratic penalty centered on this age
    social_network_coef: float = 1_800.0
    ability_coef: float = 2_500.0         # deliberate hidden confounder -- see class docstring
    noise_lognormal_sigma: float = 0.18   # multiplicative lognormal noise -> right-skewed income
    hours_per_year: float = 2_080.0       # used to annualize the min_wage floor (~40hr/wk * 52wk)


@dataclass(frozen=True)
class MobilityParams:
    income_coef: float = 0.00002
    health_endowment_coef: float = 0.3
    transit_subsidy_coef: float = 0.05
    noise_std: float = 0.5


@dataclass(frozen=True)
class HealthParams:
    health_endowment_coef: float = 5.0
    income_coef: float = 0.00003
    mobility_access_coef: float = 0.4
    age_penalty_coef: float = 0.01
    age_penalty_reference: float = 30.0   # penalty only applies above this age
    noise_std: float = 1.0


@dataclass(frozen=True)
class PreferencesParams:
    income_coef: float = 0.00001
    social_network_coef: float = 0.3
    noise_std: float = 1.0


@dataclass(frozen=True)
class SCMParams:
    """All structural-equation parameters, bundled. Pass a modified instance
    to SynthCity(params=...) to recalibrate the model without touching nodes.py."""
    ability: LatentParams = field(default_factory=LatentParams)
    risk_tolerance: LatentParams = field(default_factory=LatentParams)
    health_endowment: LatentParams = field(default_factory=LatentParams)
    parental_ses: LatentParams = field(default_factory=LatentParams)
    age: AgeParams = field(default_factory=AgeParams)
    education: EducationParams = field(default_factory=EducationParams)
    social_network: SocialNetworkParams = field(default_factory=SocialNetworkParams)
    income: IncomeParams = field(default_factory=IncomeParams)
    mobility: MobilityParams = field(default_factory=MobilityParams)
    health: HealthParams = field(default_factory=HealthParams)
    preferences: PreferencesParams = field(default_factory=PreferencesParams)


DEFAULT_PARAMS = SCMParams()

# Policy / intervention nodes and their default values.
DEFAULT_POLICY: dict[str, float] = {
    "min_wage": 7.25,
    "tax_rate": 0.20,
    "transit_subsidy": 0.0,
}

# Maps each node name to the attribute on SCMParams holding its coefficients
# (used by graph.py to pass the right sub-params to each structural equation).
NODE_PARAM_ATTR: dict[str, str] = {
    "ability": "ability",
    "risk_tolerance": "risk_tolerance",
    "health_endowment": "health_endowment",
    "parental_ses": "parental_ses",
    "age": "age",
    "education": "education",
    "social_network_position": "social_network",
    "income": "income",
    "mobility_access": "mobility",
    "health": "health",
    "preferences": "preferences",
}