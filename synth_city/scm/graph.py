"""
SynthCity: a structural causal model over a synthetic population.

    city = SynthCity(n_people=2000, seed=0)
    observational_df = city.sample()

    city_hi_wage = city.do(min_wage=15.0)      # ground-truth intervention
    interventional_df = city_hi_wage.sample()

    true_ate = interventional_df["income"].mean() - observational_df["income"].mean()

Because every structural equation is known (see nodes.py), `true_ate`
above is the *actual* causal effect, not an estimate -- this is what
Stage 2 estimators (propensity scores, IPTW, DML, ...) get graded against.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd

from .nodes import NODE_SPECS, POLICY_NODES


class SynthCity:
    def __init__(
        self,
        n_people: int = 2_000,
        seed: int = 0,
        policy: dict | None = None,
    ):
        self.n = n_people
        self.seed = seed
        self.policy = {**POLICY_NODES, **(policy or {})}
        self._dag = self._build_dag()
        self._order = list(nx.topological_sort(self._dag))

    # ------------------------------------------------------------------
    def _build_dag(self) -> nx.DiGraph:
        g = nx.DiGraph()
        g.add_nodes_from(self.policy.keys())
        for node, (_, parents) in NODE_SPECS.items():
            g.add_node(node)
            for parent in parents:
                g.add_edge(parent, node)
        return g

    @property
    def dag(self) -> nx.DiGraph:
        """The DAG structure (networkx.DiGraph), for inspection/visualization."""
        return self._dag

    # ------------------------------------------------------------------
    def do(self, **overrides: float) -> "SynthCity":
        """
        Return a NEW SynthCity with the given policy nodes fixed to
        constants, leaving self unmodified. This is the do()-operator:
        it severs the fixed node from its normal (nonexistent, since
        policy nodes have no structural equation of their own) parents
        and sets it to a constant for every person.
        """
        unknown = set(overrides) - set(self.policy)
        if unknown:
            raise ValueError(f"Not a policy node: {sorted(unknown)}")
        return SynthCity(n_people=self.n, seed=self.seed, policy={**self.policy, **overrides})

    # ------------------------------------------------------------------
    def sample(self) -> pd.DataFrame:
        """Draw n_people from the SCM under the current policy. Deterministic given seed."""
        rng = np.random.default_rng(self.seed)
        values: dict[str, np.ndarray] = {}

        for node in self._order:
            if node in self.policy:
                values[node] = np.full(self.n, self.policy[node], dtype=float)
                continue
            func, parents = NODE_SPECS[node]
            kwargs = {p: values[p] for p in parents}
            values[node] = func(rng, self.n, **kwargs)

        return pd.DataFrame(values)

    def __repr__(self) -> str:
        return f"SynthCity(n_people={self.n}, seed={self.seed}, policy={self.policy})"
