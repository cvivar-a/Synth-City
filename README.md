# Synth-City

A synthetic city simulation framework for benchmarking causal inference methods, data science techniques,experimentation, marketing mix modeling, and game-theory auctions — with known ground truth, because the population is generated from a structural causal model rather than collected.



## Quantitative analysis

Write-ups with results and figures, organized by domain: quantitative_analysis/

Causal inference — What actually happens though out the city when interventions happend. Ground-truth intervention effects, and how close standard estimators get to that truth from observational data alone. Methods: propensity scores, IPTW, doubly robust estimation, causal forests, double machine learning (DML).

DS — Exploratory analysis and predictive modeling on the simulated population, the kind of day-to-day analysis work that sits alongside causal questions. 
Methods: EDA, feature engineering, standard ML models, model evaluation.

MMM (marketing mix modeling) — Which channel — price, promotion, or advertising — actually drove a sale, and how should a marketing budget be split across them? Methods: media mix regression, adstock/saturation transforms, Shapley-value channel attribution.

Game theory — People and businesses in this city aren't passive; they react strategically to each other and to policy. How do businesses set prices when they're competing for the same customers? How do you design a subsidy so people reveal their true preferences instead of gaming it? Methods: Nash equilibrium pricing games, mechanism design, Shapley value attribution (the same tool used for MMM budget splits, applied here to cooperative payoff allocation).

### Core simulator

The people-level structural causal model (SCM), its do() operator for ground-truth interventions, and a homophilous social graph generator live in synth_city/.

bash
pip install -r requirements.txt
python -m synth_city.data.generate --n 5000 --seed 0 --out city.csv
pytest tests/ -v


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

### Roadmap
See synth_city_architecture.md for the full design — this repo currently implements Stage 1 (the simulator); Stages 2–4 (estimators, learned behavioral agents, and RL over city policy) are in progress.




