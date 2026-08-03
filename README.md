# Synth-City
A synthetic city simulation framework for benchmarking causal inference methods and experimentation. 


# Synth City — Stage 1 scaffold

A synthetic city for benchmarking causal inference, experimentation, and
policy learning. This is the Stage 1 scaffold: the people-level structural
causal model (SCM), its `do()`-operator for ground-truth interventions,
and a basic homophilous social graph generator.

## Install

```bash
pip install -r requirements.txt
```

## Quickstart

```python
from synth_city.scm.graph import SynthCity

city = SynthCity(n_people=5000, seed=0)
observational_df = city.sample()

# Ground-truth intervention: what happens if min wage goes to $15?
treated_city = city.do(min_wage=15.0)
interventional_df = treated_city.sample()

true_ate = interventional_df["income"].mean() - observational_df["income"].mean()
print(f"true ATE on mean income: {true_ate:,.2f}")
```

Or from the command line:

```bash
python -m synth_city.data.generate --n 5000 --seed 0 --out city.csv
```

## Run tests

```bash
pytest tests/ -v
```

## Project layout

```
synth_city/
  scm/
    nodes.py          # each node's structural equation (vectorized numpy)
    graph.py           # SynthCity class: DAG, topological sampling, do()
  network/
    social_graph.py    # SES-homophilous social graph (stochastic block model)
  data/
    generate.py         # CLI: sample a city, demo a ground-truth ATE
tests/
  test_acyclicity.py               # DAG is a DAG, sampling is deterministic
  test_intervention_consistency.py  # do() moves outcomes in the right direction
```

## What's next

- **Stage 1b**: unroll this into a time-indexed (dynamic Bayesian network)
  version so income/health/mobility feedback loops work across periods.
- **Stage 2**: fit propensity scores / IPTW / causal forests / DML on
  `observational_df` only, and compare estimates to `true_ate` above.
- **Stage 3**: replace one or more `f_*` functions in `nodes.py` with a
  learned model (start with `social_network_position` via a GNN over the
  graph from `network/social_graph.py`).
- **Stage 4**: wrap `SynthCity` in a `gymnasium.Env` where `step(action)`
  calls `.do(**action)` and the reward is a function of the sampled
  city-level aggregates.

See `synth_city_architecture.md` for the full 4-stage design spec.
