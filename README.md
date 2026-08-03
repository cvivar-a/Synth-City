
# SynthCity- A synthetic city for solving real business problems with data

SynthCity is a simulation platform that generates realistic populations, businesses, and consumer behavior from a Structural Causal Model (SCM). Because every decision in the city is generated—not observed—the true causal relationships are known.
The project serves as a sandbox for building and evaluating end-to-end data science workflows across experimentation, causal inference, forecasting, marketing analytics, pricing, and strategic decision making.

---

## Why SynthCity?

Real-world data has important limitations:

- Counterfactual outcomes are never observed.
- Ground truth treatment effects are unknown.
- Business decisions influence customer behavior, which changes future data.

SynthCity removes these limitations while preserving realistic complexity.

Every customer, business, and interaction is generated from a Structural Causal Model, allowing interventions to be simulated and evaluated against the true underlying effects.

---

# Business Applications

Each application answers a practical business question.

| Domain | Business Question |
|---------|------------------|
| 📈 Causal Inference | Did the intervention or campaign actually cause the observed change? |
| 📊 Data Science | Which customers are most likely to purchase, churn, or respond to an offer? |
| 💰 Marketing Analytics | Which marketing channels generated incremental sales, and how should budget be allocated? |
| 🏪 Pricing & Competition | How do competing businesses adjust prices, and what pricing strategy maximizes revenue? |

---

## Causal Inference

**Question**

A city introduces a transportation subsidy.

Did it actually increase employment, or were employed people simply more likely to receive it?

Example analyses include:

- Estimating treatment effects
- Evaluating policy interventions
- Comparing observational estimates against ground truth
- Heterogeneous treatment effects

Methods

- Propensity Scores
- IPTW
- Doubly Robust Estimation
- Double Machine Learning
- Causal Forests

---

## Data Science

**Question**

Which customers are most likely to become loyal shoppers?

Example analyses include:

- Customer segmentation
- Predictive modeling
- Feature engineering
- Model evaluation
- Explainability

Methods

- XGBoost
- Random Forests
- Logistic Regression
- SHAP
- Cross Validation

---

## Marketing Analytics

**Question**

Should the company invest in advertising, promotions, or pricing?

Example analyses include:

- Marketing Mix Modeling
- Channel attribution
- Incrementality analysis
- Budget optimization

Methods

- Media Mix Regression
- Adstock Models
- Saturation Functions
- Shapley Attribution

---

## Pricing & Strategic Decision Making

**Question**

What happens when multiple businesses compete for the same customers?

Example analyses include:

- Competitive pricing
- Auction simulations
- Market equilibrium
- Policy design

Methods

- Nash Equilibrium
- Mechanism Design
- Cooperative Game Theory
- Shapley Value

---

# Repository Structure

```text

### Project structure
synth_city/
├── synth_city/              # core package: SCM, DAG, do(), social graph
├── tests/
├── quantitative_analysis/
│   ├── causal-inference/
│   ├── ds/
│   ├── mmm/
│   ├── game-theory/
│   └── README.md
└── requirements.txt
```

---

# Quick Start

```bash
pip install -r requirements.txt

python -m synth_city.data.generate \
    --n 5000 \
    --seed 0 \

pytest tests/ -v
```

---

# Roadmap

Current focus

- ✅ Structural Causal Model
- ✅ Synthetic population generation
- ✅ Ground-truth interventions
- ✅ Social network generation

Coming next

- Customer behavior simulation
- Business strategy simulation
- Marketing campaigns
- Dynamic pricing
- Reinforcement learning agents
- City-wide policy optimization

---

## Motivation

By combining causal simulation with realistic consumer behavior, the project provides a controlled environment for developing practical data science solutions before applying them to real-world problems.

