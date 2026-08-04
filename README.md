
# SynthCity

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
| 📈 ![Causal Inference](https://github.com/cvivar-a/Synth-City/tree/main/quantitative_anaysis/causal_inference) | Did the intervention or campaign actually cause the observed change? |
| 📊 Data Science | Which customers are most likely to purchase, churn, or respond to an offer? |
| 💰 Marketing Analytics | Which marketing channels generated incremental sales, and how should budget be allocated? |
| 🏪 Pricing & Competition | How do competing businesses adjust prices, and what pricing strategy maximizes revenue? |



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
