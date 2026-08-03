import networkx as nx

from synth_city.scm.graph import SynthCity


def test_dag_is_acyclic():
    city = SynthCity(n_people=10, seed=0)
    assert nx.is_directed_acyclic_graph(city.dag)


def test_sample_shape_and_columns():
    city = SynthCity(n_people=250, seed=0)
    df = city.sample()
    assert len(df) == 250
    expected_cols = {
        "ability",
        "risk_tolerance",
        "health_endowment",
        "parental_ses",
        "age",
        "education",
        "social_network_position",
        "income",
        "mobility_access",
        "health",
        "preferences",
        "min_wage",
        "tax_rate",
        "transit_subsidy",
    }
    assert expected_cols.issubset(set(df.columns))


def test_sampling_is_deterministic_given_seed():
    city_a = SynthCity(n_people=100, seed=42)
    city_b = SynthCity(n_people=100, seed=42)
    df_a = city_a.sample()
    df_b = city_b.sample()
    assert df_a.equals(df_b)
