"""Compara P, PI e PID no motor DC (resposta ao degrau) e imprime métricas."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pidsim import PID, dc_motor, simulate, step_metrics

TUNINGS = {
    "P":   dict(kp=100),
    "PI":  dict(kp=100, ki=200),
    "PID": dict(kp=100, ki=200, kd=10),
}
U_LIM = 12.0  # V

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
print(f"{'':4}{'OS %':>8}{'tr (s)':>9}{'ts (s)':>9}{'ess':>9}{'IAE':>8}")
for name, gains in TUNINGS.items():
    res = simulate(dc_motor(), PID(**gains, u_min=-U_LIM, u_max=U_LIM), 1.0, t_end=3)
    m = step_metrics(res)
    print(f"{name:4}{m['overshoot_pct']:8.2f}{m['rise_time_s']:9.3f}"
          f"{m['settling_time_s']:9.3f}{m['steady_state_error']:9.4f}{m['IAE']:8.4f}")
    ax1.plot(res.t, res.y, label=name)
    ax2.plot(res.t, res.u, label=name)

ax1.axhline(1.0, color="k", ls="--", lw=0.8, label="referência")
ax1.set_ylabel("velocidade (rad/s)"); ax1.legend(); ax1.grid(alpha=0.3)
ax2.set_ylabel("tensão (V)"); ax2.set_xlabel("tempo (s)"); ax2.grid(alpha=0.3)
ax1.set_title("Motor DC: P vs PI vs PID")
out = Path(__file__).resolve().parent.parent / "docs" / "compare_tunings.png"
fig.tight_layout(); fig.savefig(out, dpi=150)
print(f"Figura salva em {out}")
