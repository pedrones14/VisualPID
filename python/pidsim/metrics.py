"""Métricas de desempenho para resposta ao degrau."""
from __future__ import annotations

import numpy as np

from .simulate import Result


def _first_crossing(t, y, level):
    idx = np.flatnonzero(y >= level)
    return t[idx[0]] if idx.size else np.nan


def step_metrics(res: Result, tol: float = 0.02) -> dict:
    """Sobressinal (%), tempo de subida 10–90 %, acomodação (±tol),
    erro em regime e integrais IAE / ISE. Assume degrau positivo."""
    t, y, r = res.t, res.y, res.r
    r_f = r[-1]
    e = r - y
    overshoot = max(0.0, (y.max() - r_f) / abs(r_f) * 100.0)

    t10 = _first_crossing(t, y, 0.1 * r_f)
    t90 = _first_crossing(t, y, 0.9 * r_f)
    rise = t90 - t10

    outside = np.flatnonzero(np.abs(y - r_f) > tol * abs(r_f))
    if outside.size == 0:
        settling = 0.0
    elif outside[-1] >= len(t) - 1:
        settling = np.nan  # não acomodou
    else:
        settling = t[outside[-1] + 1]

    tail = max(1, len(y) // 20)
    return {
        "overshoot_pct": overshoot,
        "rise_time_s": rise,
        "settling_time_s": settling,
        "steady_state_error": float(np.mean(e[-tail:])),
        "IAE": float(np.trapezoid(np.abs(e), t)),
        "ISE": float(np.trapezoid(e**2, t)),
    }
