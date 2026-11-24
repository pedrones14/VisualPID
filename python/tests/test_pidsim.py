from pidsim import PID, dc_motor, first_order, simulate, step_metrics


def test_p_only_steady_state_error_matches_theory():
    plant = first_order(K=2.0, tau=1.0)
    res = simulate(plant, PID(kp=4.0), 1.0, t_end=10)
    expected = 1 / (1 + 4.0 * 2.0)          # 1 / (1 + Kp*K)
    assert abs(res.r[-1] - res.y[-1] - expected) < 1e-3


def test_pi_removes_steady_state_error():
    res = simulate(dc_motor(), PID(kp=20, ki=40), 1.0, t_end=10)
    assert abs(step_metrics(res)["steady_state_error"]) < 1e-3


def test_output_respects_saturation():
    res = simulate(dc_motor(), PID(kp=100, ki=200, u_min=-12, u_max=12), 1.0, t_end=5)
    assert res.u.max() <= 12 + 1e-9 and res.u.min() >= -12 - 1e-9


def test_anti_windup_reduces_overshoot():
    kw = dict(kp=100, ki=300, u_min=-12, u_max=12)
    with_aw = simulate(dc_motor(), PID(**kw, anti_windup=True), 1.0, t_end=15)
    without = simulate(dc_motor(), PID(**kw, anti_windup=False), 1.0, t_end=15)
    assert step_metrics(with_aw)["overshoot_pct"] < step_metrics(without)["overshoot_pct"]


def test_disturbance_rejected_by_integral_action():
    res = simulate(first_order(), PID(kp=5, ki=10), 1.0, t_end=20,
                   disturbance=lambda t: 0.5 if t > 8 else 0.0)
    assert abs(res.y[-1] - 1.0) < 1e-2


def test_p_only_keeps_integrator_at_zero_even_when_saturated():
    # Regressão: com ki=0 o anti-windup não pode alimentar o integrador.
    # Motor DC: ganho DC = K/(bR+K^2); erro em regime do P = 1/(1+Kp*G0).
    plant = dc_motor()
    res = simulate(plant, PID(kp=100, u_min=-12, u_max=12), 1.0, t_end=5)
    expected = 1 / (1 + 100 * plant.dc_gain())
    assert abs(res.r[-1] - res.y[-1] - expected) < 1e-3
