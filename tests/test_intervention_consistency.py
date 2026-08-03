from synth_city.scm.graph import SynthCity


def test_min_wage_increase_raises_mean_income():
    city = SynthCity(n_people=5_000, seed=1)
    baseline = city.sample()
    treated = city.do(min_wage=20.0).sample()
    assert treated["income"].mean() >= baseline["income"].mean()


def test_higher_tax_rate_lowers_mean_income():
    city = SynthCity(n_people=5_000, seed=1)
    baseline = city.sample()
    treated = city.do(tax_rate=0.60).sample()
    assert treated["income"].mean() < baseline["income"].mean()


def test_do_does_not_mutate_original_city():
    city = SynthCity(n_people=100, seed=1)
    original_policy = dict(city.policy)
    _ = city.do(tax_rate=0.9, min_wage=25.0)
    assert city.policy == original_policy


def test_do_rejects_unknown_node():
    city = SynthCity(n_people=10, seed=0)
    try:
        city.do(not_a_real_policy=1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("do() should reject unknown policy node names")
