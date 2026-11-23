"""Laço fechado: planta + controlador."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Union

import numpy as np

Signal = Union[float, Callable[[float], float]]


@dataclass
class Result:
    t: np.ndarray
    r: np.ndarray   # referência
    y: np.ndarray   # saída da planta
    u: np.ndarray   # sinal de controle


def _as_fn(s: Signal | None) -> Callable[[float], float]:
    if s is None:
        return lambda t: 0.0
    return s if callable(s) else (lambda t, v=float(s): v)


def simulate(plant, controller, setpoint: Signal, t_end: float,
             disturbance: Signal | None = None, noise_std: float = 0.0,
             seed: int = 0) -> Result:
    """Simula o laço fechado.

    disturbance: somado à entrada da planta (perturbação de carga).
    noise_std:   ruído gaussiano na medição.
    """
    dt = plant.dt
    controller.dt = dt
    controller.reset()
    plant.reset()
    r_fn, d_fn = _as_fn(setpoint), _as_fn(disturbance)
    rng = np.random.default_rng(seed)

    n = int(round(t_end / dt))
    t = np.arange(n) * dt
    r, y, u = np.zeros(n), np.zeros(n), np.zeros(n)
    for k in range(n):
        r[k] = r_fn(t[k])
        y[k] = plant.output()
        y_meas = y[k] + (rng.normal(0.0, noise_std) if noise_std else 0.0)
        u[k] = controller.update(r[k], y_meas)
        plant.step(u[k] + d_fn(t[k]))
    return Result(t, r, y, u)
