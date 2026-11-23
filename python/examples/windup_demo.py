"""Mostra o efeito do windup da integral com e sem anti-windup."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pidsim import PID, dc_motor, simulate, step_metrics

kw = dict(kp=100, ki=300, u_min=-12, u_max=12)
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
for aw, label in [(False, "sem anti-windup"), (True, "com anti-windup")]:
    res = simulate(dc_motor(), PID(**kw, anti_windup=aw), 1.0, t_end=6)
    print(f"{label:18} sobressinal = {step_metrics(res)['overshoot_pct']:.2f} %")
    ax1.plot(res.t, res.y, label=label)
    ax2.plot(res.t, res.u, label=label)
ax1.axhline(1.0, color="k", ls="--", lw=0.8)
ax1.set_ylabel("velocidade (rad/s)"); ax1.legend(); ax1.grid(alpha=0.3)
ax2.set_ylabel("tensão (V)"); ax2.set_xlabel("tempo (s)"); ax2.grid(alpha=0.3)
ax1.set_title("Windup da integral (saturação de ±12 V)")
out = Path(__file__).resolve().parent.parent / "docs" / "windup_demo.png"
fig.tight_layout(); fig.savefig(out, dpi=150)
print(f"Figura salva em {out}")
