"""
"Who actually benefits from raising the minimum wage?"

Break the aggregate ATE down by subgroup (education tier, age bracket) to
turn one flat number into a story about who the policy helps most.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from synth_city.scm.graph import SynthCity

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
fig.savefig("quantitative_analysis/causal-inference/direct-intervention-effects/figures/subgroup_effects.png", dpi=150, bbox_inches="tight")

print("overall ATE:", round(overall_ate, 2))
print(edu_ate.to_string(index=False))
print(age_ate.to_string(index=False))
