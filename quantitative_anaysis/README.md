# Quantitative Analysis

This repository contains a collection of end-to-end analytical case studies built on **SynthCity**.

Each study starts with a practical business or policy question, analyzes synthetic observational data, and compares the conclusions against the simulator's known ground truth whenever possible.

Every analysis is self-contained and includes:

- reproducible code .py
- A written report summarizing the findings with figures

Although the data are simulated, every workflow mirrors the process used in real-world analytics projects—from exploratory analysis and modeling to interpretation and decision-making.

---

# Analysis Domains

## Causal Inference

**Question**

Did an intervention actually cause the observed outcome, or are we only seeing a correlation?

Typical case studies include:

- Public policy evaluation
- Pricing interventions
- Transportation and infrastructure programs
- Healthcare and education policies
- Customer incentives and promotions

| Analysis | Business Question | Report |
|----------|-------------------|--------|
| Minimum Wage Effect | Does increasing the minimum wage improve household income after accounting for selection bias? | [Results](causal_inference/minimum_wage_effect/results.md) |
| Transportation Subsidy | Does subsidized public transport increase employment? | *(Coming Soon)* |
| Vaccination Campaign | Does a public health campaign improve long-term outcomes? | *(Coming Soon)* |

---

## Data Science

**Question**

What can we learn from the city's data, and how can those insights support better decisions?

Typical case studies include:

- Customer segmentation
- Demand forecasting
- Churn prediction
- Fraud detection
- Recommendation systems
- Predictive modeling

| Analysis | Business Question | Report |
|----------|-------------------|--------|
| Customer Lifetime Value | Which customer characteristics best predict future spending? | *(Coming Soon)* |
| Retail Demand Forecasting | Can future product demand be predicted across neighborhoods? | *(Coming Soon)* |
| Customer Segmentation | What distinct consumer groups emerge from purchasing behavior? | *(Coming Soon)* |

---

## Marketing Analytics

**Question**

Which marketing activities generated incremental value, and where should future budget be invested?

Typical case studies include:

- Marketing Mix Modeling
- Campaign effectiveness
- Incrementality
- Channel attribution
- Budget optimization

| Analysis | Business Question | Report |
|----------|-------------------|--------|
| Marketing Mix Model | Which combination of advertising, pricing, and promotions drives sales? | *(Coming Soon)* |
| Promotion Effectiveness | Do discounts increase long-term revenue or only short-term purchases? | *(Coming Soon)* |
| Media Attribution | Which channels deserve credit for conversions? | *(Coming Soon)* |

---

## Pricing & Competition

**Question**

How do businesses adapt their strategies when competitors and customers respond to every decision?

Typical case studies include:

- Dynamic pricing
- Competitive strategy
- Auctions
- Market equilibrium
- Policy design

| Analysis | Business Question | Report |
|----------|-------------------|--------|
| Dynamic Pricing | How should competing retailers adjust prices over time? | *(Coming Soon)* |
| Advertising Auction | How do different bidding strategies affect advertiser performance? | *(Coming Soon)* |
| Market Entry | What happens when a new competitor enters the market? | *(Coming Soon)* |

---

# Reproducibility

Every report is fully reproducible from the accompanying .py file.
