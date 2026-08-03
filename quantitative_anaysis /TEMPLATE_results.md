# [Experiment title]

**Status:** ☐ draft ☐ in progress ☑ complete
**Date:** YYYY-MM-DD
**Notebook:** [`notebook.ipynb`](./notebook.ipynb)

## Objective

One or two sentences: what question is this experiment answering, and why does it matter?
e.g. *"What is the true causal effect of raising the minimum wage on income, and does it
propagate downstream to health and mobility?"*

## Method

- **Population:** n = _____, seed = _____
- **Intervention:** `do(______ = ______)`
- **Estimator(s) used (if Stage 2+):** e.g. propensity score matching, IPTW, causal forest
- Any other relevant config (policy defaults, model hyperparameters, etc.)

## Key results

### [Result 1 title]

![description](./figures/figure1.png)

One or two sentences interpreting the figure — what should the reader notice?

### [Result 2 title]

![description](./figures/figure2.png)

Interpretation.

## Headline numbers

| Metric | Value |
|---|---|
| True ATE | |
| Estimated ATE (if applicable) | |
| Estimator bias | |

## Interpretation

2-4 sentences: what did you learn? Does it match intuition? Anything surprising?

## Reproduce

```bash
jupyter lab experiments/[folder]/notebook.ipynb
```
