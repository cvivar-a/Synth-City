"""
Policy sensitivity tornado chart: for each policy lever (min_wage, tax_rate,
transit_subsidy), sweep it across a realistic range holding the others at
default, and measure the resulting swing in mean income. Sort by swing size
so the most impactful lever is on top -- the classic "tornado" shape.
"""
import matplotlib.pyplot as plt
import numpy as np

from synth_city.scm.graph import SynthCity

N = 8_000
SEED = 0

base_city = SynthCity(n_people=N, seed=SEED)
baseline_income = base_city.sample()["income"].mean()

levers = {
    "min_wage": (7.25, 20.0),
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
fig.savefig("quantitative_analysis/causal-inference/direct-intervention-effects/figures/tornado_income.png", dpi=150, bbox_inches="tight")

print("baseline mean income:", round(baseline_income, 2))
for r in results:
    print(f"{r['lever']:16s} swing=${r['swing']:,.2f}  ({r['lo_val']}\u2192{r['income_lo']:,.0f}, {r['hi_val']}\u2192{r['income_hi']:,.0f})")
