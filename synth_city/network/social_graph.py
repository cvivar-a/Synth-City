"""
Builds a social graph over an already-sampled population, with homophily
on parental_ses (people connect more within their SES tier than across).

This is deliberately separate from the SCM in scm/graph.py: the graph
is generated *from* a sampled DataFrame, and `social_network_position`
(a summary statistic, e.g. degree) can optionally be fed back in as a
node input for more advanced versions of the DAG. For Stage 1, the SCM
node `social_network_position` is a standalone approximation; this
module is what you'd swap in for a more realistic Stage 1b / Stage 3.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd


def build_social_graph(
    df: pd.DataFrame,
    n_blocks: int = 5,
    p_within: float = 0.05,
    p_between: float = 0.005,
    seed: int = 0,
) -> nx.Graph:
    """
    Stochastic block model graph: people are bucketed into `n_blocks`
    tiers by parental_ses, connect with probability `p_within` to others
    in the same tier and `p_between` to people in other tiers. Produces
    the SES-homophily you'd expect in a real social network.
    """
    blocks = pd.qcut(df["parental_ses"], n_blocks, labels=False, duplicates="drop")
    n_actual_blocks = int(blocks.nunique())
    sizes = blocks.value_counts().sort_index().tolist()

    probs = np.full((n_actual_blocks, n_actual_blocks), p_between)
    np.fill_diagonal(probs, p_within)

    g = nx.stochastic_block_model(sizes, probs.tolist(), seed=seed)

    # Map graph node ids back to the DataFrame's index so you can join
    # graph-derived features (degree, clustering, ...) back onto df.
    order = blocks.sort_values(kind="stable").index.tolist()
    mapping = {i: order[i] for i in range(len(order))}
    return nx.relabel_nodes(g, mapping)
