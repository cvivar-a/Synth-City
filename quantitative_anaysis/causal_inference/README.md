
# Synth City — Quantitative analysis

This is the people-level structural
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