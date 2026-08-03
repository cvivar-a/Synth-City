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

 
N = 10_000
SEED = 0
 
# Nodes worth plotting as distributions (excludes policy nodes -- those are
# constants under a given policy, not distributions, so a histogram of them
# is just a spike and not informative).
STOCHASTIC_NODES = [
    "ability", "risk_tolerance", "health_endowment", "parental_ses", "age",
    "education", "social_network_position", "income", "mobility_access",
    "health", "preferences",
]
 
LATENT_NODES = {"ability", "risk_tolerance", "health_endowment", "parental_ses", "age"}
 
city = SynthCity(n_people=N, seed=SEED)
df = city.sample()
 
fig, axes = plt.subplots(4, 3, figsize=(13, 12))
axes = axes.flatten()
 
for ax, node in zip(axes, STOCHASTIC_NODES):
    color = "#8172B2" if node in LATENT_NODES else "#4C72B0"
    ax.hist(df[node], bins=40, color=color)
    ax.set_title(node, fontsize=11)
    ax.set_ylabel("count", fontsize=8)
    ax.tick_params(labelsize=8)
 
# hide the unused 12th subplot slot, and use it for a tiny legend instead
axes[-1].axis("off")
axes[-1].text(0.0, 0.7, "\u25A0 latent / exogenous", color="#8172B2", fontsize=11, transform=axes[-1].transAxes)
axes[-1].text(0.0, 0.5, "\u25A0 endogenous", color="#4C72B0", fontsize=11, transform=axes[-1].transAxes)
axes[-1].text(0.0, 0.25, f"n = {N:,}\nseed = {SEED}\npolicy = default", fontsize=9, transform=axes[-1].transAxes)
 
fig.suptitle("Synth City \u2014 marginal distribution of every SCM node", fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(os.path.join(FIGURES_DIR, "node_distributions.png"), dpi=150, bbox_inches="tight")
 
# ---------------------------------------------------------------------------
# Summary stats table
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Summary stats table
# ---------------------------------------------------------------------------
summary = df[STOCHASTIC_NODES].describe().T[["mean", "std", "min", "max"]]
summary.insert(0, "type", ["latent" if n in LATENT_NODES else "endogenous" for n in STOCHASTIC_NODES])
for col in ["mean", "std", "min", "max"]:
    summary[col] = summary[col].map(lambda x: f"{x:,.2f}")
print(summary)
 
# render the table as a PNG instead of a CSV
n_rows, n_cols = summary.shape
fig_table, ax_table = plt.subplots(figsize=(8, 0.45 * n_rows + 1))
ax_table.axis("off")
 
cell_text = summary.reset_index().rename(columns={"index": "node"}).values
col_labels = ["node", "type", "mean", "std", "min", "max"]
 
table = ax_table.table(
    cellText=cell_text,
    colLabels=col_labels,
    cellLoc="center",
    loc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.auto_set_column_width(col=list(range(len(col_labels))))
table.scale(1, 1.5)
 
# color the header row and alternate row shading for readability
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor("#6fbef2")
        cell.set_text_props(color="white", weight="bold")
    elif row % 2 == 0:
        cell.set_facecolor("#fcfeff")
 
ax_table.set_title("Synth City \u2014 node summary statistics", fontsize=12, pad=12)
fig_table.tight_layout()
fig_table.savefig(os.path.join(FIGURES_DIR, "node_summary_stats.png"), dpi=150, bbox_inches="tight")
 
print(f"\nfigure saved to {os.path.join(FIGURES_DIR, 'node_distributions.png')}")
print(f"stats table saved to {os.path.join(FIGURES_DIR, 'node_summary_stats.png')}")
 