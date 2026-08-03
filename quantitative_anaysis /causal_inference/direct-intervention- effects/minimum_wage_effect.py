"""
Ground-truth effect of raising the minimum wage: distribution shift, dose-response
curve across wage levels, and how the shock propagates through the rest of the DAG.

Because Synth City is a known structural causal model, "true_ate" below is not an
estimate -- it's the actual causal effect, computed by sampling the SAME population
under two different policies. This is the number every Stage 2 estimator (propensity
scores, IPTW, DML, ...) is graded against elsewhere in this repo.
"""
import os

import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from synth_city.scm.graph import SynthCity

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

N = 5_000
SEED = 0
MIN_WAGE_TREATMENT = 15.0

# ---------------------------------------------------------------------------
# 1. Generate the city and the intervention
# ---------------------------------------------------------------------------
city = SynthCity(n_people=N, seed=SEED)
baseline_df = city.sample()

treated_city = city.do(min_wage=MIN_WAGE_TREATMENT)
treated_df = treated_city.sample()

true_ate = treated_df["income"].mean() - baseline_df["income"].mean()
print(f"true_ate (single sample, n={N}): {true_ate:,.2f}")

# ---------------------------------------------------------------------------
# 2. Income distribution shift
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(baseline_df["income"], bins=50, alpha=0.6, label="baseline ($7.25 min wage)")
ax.hist(treated_df["income"], bins=50, alpha=0.6, label=f"treated (${MIN_WAGE_TREATMENT:.2f} min wage)")
ax.axvline(baseline_df["income"].mean(), color="C0", linestyle="--")
ax.axvline(treated_df["income"].mean(), color="C1", linestyle="--")
ax.set_xlabel("annual income")
ax.set_ylabel("count")
ax.legend()
ax.set_title(f"True ATE = ${true_ate:,.0f}")
fig.savefig(os.path.join(FIGURES_DIR, "income_distribution_shift.png"), dpi=150, bbox_inches="tight")

# ---------------------------------------------------------------------------
# 3. Dose-response curve across wage levels
# ---------------------------------------------------------------------------
wage_levels = np.arange(7.25, 25, 1.0)
mean_incomes = [city.do(min_wage=w).sample()["income"].mean() for w in wage_levels]

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(wage_levels, mean_incomes, marker="o")
ax.set_xlabel("min_wage")
ax.set_ylabel("mean income")
ax.set_title("True dose-response curve: min_wage \u2192 mean income")
fig.savefig(os.path.join(FIGURES_DIR, "min_wage_dose_response.png"), dpi=150, bbox_inches="tight")

# ---------------------------------------------------------------------------
# 4. The DAG itself
# ---------------------------------------------------------------------------
pos = nx.spring_layout(city.dag, seed=0)

fig, ax = plt.subplots(figsize=(8, 6))
nx.draw(city.dag, pos, ax=ax, with_labels=True, node_color="lightblue",
        node_size=2000, font_size=8, arrowsize=15)
fig.savefig(os.path.join(FIGURES_DIR, "dag_structure.png"), dpi=150, bbox_inches="tight")

# ---------------------------------------------------------------------------
# 5. How the shock propagates through the DAG (effect size at every node)
# ---------------------------------------------------------------------------
def compute_shifts(baseline_df, treated_df):
    shifts = {}
    for col in baseline_df.columns:
        base_mean, treat_mean = baseline_df[col].mean(), treated_df[col].mean()
        base_std = baseline_df[col].std()
        delta = treat_mean - base_mean
        effect_size = delta / base_std if base_std > 0 else 0.0
        shifts[col] = {"delta": delta, "effect_size": effect_size}
    return shifts


shifts = compute_shifts(baseline_df, treated_df)

intervened_nodes = {"min_wage"}
effect_sizes = {n: shifts[n]["effect_size"] for n in city.dag.nodes}
max_abs = max(abs(v) for k, v in effect_sizes.items() if k not in intervened_nodes) or 1

norm = mcolors.TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
cmap = cm.RdBu_r
node_colors = [
    "gold" if n in intervened_nodes else cmap(norm(effect_sizes[n]))
    for n in city.dag.nodes
]

fig, ax = plt.subplots(figsize=(9, 7))
nx.draw_networkx_edges(city.dag, pos, ax=ax, arrowsize=15, alpha=0.5)
nx.draw_networkx_nodes(city.dag, pos, ax=ax, node_color=node_colors,
                        node_size=2200, edgecolors="black", linewidths=1)
nx.draw_networkx_labels(city.dag, pos, ax=ax, font_size=8)
for n, (x, y) in pos.items():
    ax.text(x, y - 0.08, f"\u0394={shifts[n]['delta']:+.2f}", fontsize=7, ha="center", color="dimgray")

sm = cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
fig.colorbar(sm, ax=ax, shrink=0.7, label="standardized effect size")
ax.set_title(f"DAG shift under do(min_wage={MIN_WAGE_TREATMENT})  [gold = intervened node]")
ax.axis("off")
fig.savefig(os.path.join(FIGURES_DIR, "dag_shift_min_wage.png"), dpi=150, bbox_inches="tight")

# ---------------------------------------------------------------------------
# 6. Stabilize the true ATE across seeds (single-sample ATE has sampling noise)
# ---------------------------------------------------------------------------
n_seeds = 20
ates = [
    SynthCity(n_people=N, seed=s).do(min_wage=MIN_WAGE_TREATMENT).sample()["income"].mean()
    - SynthCity(n_people=N, seed=s).sample()["income"].mean()
    for s in range(n_seeds)
]
true_ate_stable = np.mean(ates)
true_ate_std = np.std(ates)
print(f"true_ate averaged over {n_seeds} seeds: {true_ate_stable:,.2f} \u00b1 {true_ate_std:,.2f}")
