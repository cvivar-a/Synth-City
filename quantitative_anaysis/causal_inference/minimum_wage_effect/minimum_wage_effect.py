import sys, os

import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

'''
Set pathway for calling Synth City:
'''
def find_project_root(marker="requirements.txt"):
    path = os.getcwd()
    while path != os.path.dirname(path):  # stop at filesystem root
        if os.path.exists(os.path.join(path, marker)):
            return path
        path = os.path.dirname(path)
    raise FileNotFoundError(f"couldn't find project root (looking for {marker})")

PROJECT_ROOT = find_project_root()
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from synth_city.scm.graph import SynthCity

'''
Set pathway for saving figures:
'''
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


"""
1)  Ground-truth effect of raising the minimum wage: distribution shift, dose-response
curve across wage levels, and how the shock propagates through the rest of the DAG.
Synth City is a known structural causal model, "true_ate" is the actual causal effect
"""

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


"""
2) Policy sensitivity tornado chart: for each policy lever (min_wage, tax_rate,
transit_subsidy), sweep it across a realistic range holding the others at
default, and measure the resulting swing in mean income. Sort by swing size
so the most impactful lever is on top -- the classic "tornado" shape.
"""

city = SynthCity(n_people=N, seed=SEED)
baseline_df = city.sample()
baseline_income = city.sample()["income"].mean()

levers = {
    "min_wage": (7.25, MIN_WAGE_TREATMENT),
    "tax_rate": (0.10, 0.45),
    "transit_subsidy": (0.0, 150.0),
}

results = []
for lever, (lo, hi) in levers.items():
    income_lo = SynthCity(n_people=N, seed=SEED, policy={lever: lo}).sample()["income"].mean()
    income_hi = SynthCity(n_people=N, seed=SEED, policy={lever: hi}).sample()["income"].mean()
    results.append({
        "lever": lever, "lo_val": lo, "hi_val": hi,
        "income_lo": income_lo, "income_hi": income_hi,
        "swing": abs(income_hi - income_lo),
    })

results.sort(key=lambda r: r["swing"])  # ascending so biggest ends up on top when plotted

fig, ax = plt.subplots(figsize=(8, 4.5))
labels = [
    f"{r['lever']}\n(${r['lo_val']:g} \u2192 ${r['hi_val']:g})" if r["lever"] != "tax_rate"
    else f"{r['lever']}\n({r['lo_val']:.0%} \u2192 {r['hi_val']:.0%})"
    for r in results
]
lows = [min(r["income_lo"], r["income_hi"]) for r in results]
highs = [max(r["income_lo"], r["income_hi"]) for r in results]
y = np.arange(len(results))

ax.barh(y, [h - l for l, h in zip(lows, highs)], left=lows, color="#4C72B0", height=0.6)
ax.axvline(baseline_income, color="gray", linestyle="--", linewidth=1, label=f"baseline mean income (${baseline_income:,.0f})")
ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.set_xlabel("mean annual income ($)")
ax.set_title("Policy sensitivity: swing in mean income by lever, low \u2192 high setting")
ax.legend(loc="lower right", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "tornado_income.png"), dpi=150, bbox_inches="tight")

print("baseline mean income:", round(baseline_income, 2))
for r in results:
    print(f"{r['lever']:16s} swing=${r['swing']:,.2f}  ({r['lo_val']}\u2192{r['income_lo']:,.0f}, {r['hi_val']}\u2192{r['income_hi']:,.0f})")


"""
"Who actually benefits from raising the minimum wage?"

Break the aggregate ATE down by subgroup (education tier, age bracket) to
turn one flat number into a story about who the policy helps most.
"""

N = 20_000  # bigger n here since we're slicing into subgroups and want stable means per slice
SEED = 0

city = SynthCity(n_people=N, seed=SEED)
baseline = city.sample()
treated = city.do(min_wage=15.0).sample()

baseline["education_tier"] = pd.cut(
    baseline["education"], bins=[6, 12, 16, 22],
    labels=["no degree (<12yr)", "bachelor's (12-16yr)", "graduate (16yr+)"], include_lowest=True,
)
baseline["age_bracket"] = pd.cut(
    baseline["age"], bins=[18, 30, 45, 60, 75],
    labels=["18-30", "30-45", "45-60", "60-75"], include_lowest=True,
)
treated["education_tier"] = baseline["education_tier"].values  # same people, same draw of latent covariates
treated["age_bracket"] = baseline["age_bracket"].values

def subgroup_ate(group_col):
    rows = []
    for grp in baseline[group_col].cat.categories:
        b = baseline.loc[baseline[group_col] == grp, "income"]
        t = treated.loc[treated[group_col] == grp, "income"]
        rows.append({"group": str(grp), "ate": t.mean() - b.mean(), "n": len(b)})
    return pd.DataFrame(rows)

edu_ate = subgroup_ate("education_tier")
age_ate = subgroup_ate("age_bracket")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

axes[0].barh(edu_ate["group"], edu_ate["ate"], color="#55A868")
axes[0].set_xlabel("ATE on annual income ($)")
axes[0].set_title("Effect by education tier")
axes[0].invert_yaxis()

axes[1].bar(age_ate["group"], age_ate["ate"], color="#4C72B0")
axes[1].set_ylabel("ATE on annual income ($)")
axes[1].set_title("Effect by age bracket")

overall_ate = treated["income"].mean() - baseline["income"].mean()
fig.suptitle(f"Who benefits from raising min_wage to $15? (overall ATE = ${overall_ate:,.0f})")
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "subgroup_effects.png"), dpi=150, bbox_inches="tight")


print("overall ATE:", round(overall_ate, 2))
print(edu_ate.to_string(index=False))
print(age_ate.to_string(index=False))


"""
Visualize the SES-homophilous social network: color nodes by parental_ses
tier and lay them out with a force-directed layout so the community
structure (people clustering with similar-background people) is visible
at a glance, plus a degree distribution as a sanity-check/companion plot.
"""

from synth_city.network.social_graph import build_social_graph

N = 200  # kept small on purpose -- a network plot of 8000 nodes is an unreadable hairball
SEED = 0

city = SynthCity(n_people=N, seed=SEED)
df = city.sample()
g = build_social_graph(df, n_blocks=5, p_within=0.06, p_between=0.004, seed=SEED)

tiers = pd.qcut(df["parental_ses"], 5, labels=False, duplicates="drop")
cmap = cm.viridis
node_colors = [cmap(tiers[n] / tiers.max()) for n in g.nodes]

pos = nx.spring_layout(g, seed=SEED, k=0.25)

fig, ax = plt.subplots(figsize=(8, 7))
nx.draw_networkx_edges(g, pos, ax=ax, alpha=0.15, width=0.6)
nx.draw_networkx_nodes(g, pos, ax=ax, node_color=node_colors, node_size=60, edgecolors="white", linewidths=0.4)
sm = cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=4))
sm.set_array([])
fig.colorbar(sm, ax=ax, label="parental SES tier (0=lowest, 4=highest)", shrink=0.8)
ax.set_title(f"Synth City social network (n={N}) \u2014 clustering by parental SES")
ax.axis("off")
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "social_network_ses.png"), dpi=150, bbox_inches="tight")

degrees = [d for _, d in g.degree()]
fig2, ax2 = plt.subplots(figsize=(6, 4))
ax2.hist(degrees, bins=20, color="#4C72B0")
ax2.set_xlabel("degree (number of connections)")
ax2.set_ylabel("count")
ax2.set_title("Degree distribution")
fig2.tight_layout()
fig2.savefig(os.path.join(FIGURES_DIR, "degree_distribution.png"), dpi=150, bbox_inches="tight")

# how much more likely are same-tier connections than cross-tier? (homophily check)
same_tier_edges = sum(1 for u, v in g.edges() if tiers[u] == tiers[v])
homophily_ratio = same_tier_edges / g.number_of_edges()
print(f"nodes={g.number_of_nodes()} edges={g.number_of_edges()}")
print(f"avg clustering coefficient: {nx.average_clustering(g):.3f}")
print(f"share of edges within the same SES tier: {homophily_ratio:.1%} (vs. ~20% under random mixing across 5 tiers)")
