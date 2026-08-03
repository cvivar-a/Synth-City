"""
Generate an observational dataset, plus a demo ground-truth intervention.

    python -m synth_city.data.generate --n 5000 --seed 0 --out city.csv
"""

from __future__ import annotations

import argparse

from synth_city.scm.graph import SynthCity


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=2_000, help="number of people")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=str, default="synth_city_sample.csv")
    parser.add_argument(
        "--min-wage-intervention",
        type=float,
        default=15.0,
        help="min_wage value to use for the ground-truth ATE demo",
    )
    args = parser.parse_args()

    city = SynthCity(n_people=args.n, seed=args.seed)
    observational_df = city.sample()
    observational_df.to_csv(args.out, index=False)
    print(f"saved {len(observational_df)} rows to {args.out}")
    print(f"columns: {list(observational_df.columns)}")

    intervened_city = city.do(min_wage=args.min_wage_intervention)
    interventional_df = intervened_city.sample()

    true_ate = interventional_df["income"].mean() - observational_df["income"].mean()
    print(
        f"\nground-truth ATE of raising min_wage from "
        f"{city.policy['min_wage']} to {args.min_wage_intervention}: "
        f"{true_ate:,.2f} (mean annual income)"
    )


if __name__ == "__main__":
    main()
