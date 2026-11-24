"""Controlador PID discreto com derivada filtrada e anti-windup."""
from __future__ import annotations

import math


class PID:
    """PID em forma paralela.

    u = kp*e + I + D
    - Derivada aplicada na *medição* (sem "derivative kick") e filtrada
      por um filtro de 1ª ordem com constante de tempo `tau_d`.
    - Saturação em [u_min, u_max].
    - Anti-windup por back-calculation (ganho `kb`); use anti_windup=False
      para ver o efeito do windup.
    """

    def __init__(self, kp, ki=0.0, kd=0.0, tau_d=0.01, u_min=-math.inf,
                 u_max=math.inf, anti_windup=True, kb=None, dt=1e-3):
        self.kp, self.ki, self.kd = float(kp), float(ki), float(kd)
        self.tau_d = float(tau_d)
        self.u_min, self.u_max = u_min, u_max
        self.anti_windup = anti_windup
        # Tt = Ti = kp/ki é uma escolha clássica para o tempo de tracking
        self.kb = kb if kb is not None else (ki / kp if kp and ki else 1.0)
        self.dt = float(dt)
        self.reset()

    def reset(self) -> None:
        self._i = 0.0
        self._d = 0.0
        self._y_prev = None

    def update(self, setpoint: float, y: float) -> float:
        dt = self.dt
        e = setpoint - y

        if self._y_prev is None:
            self._y_prev = y
        a = self.tau_d / (self.tau_d + dt)
        self._d = a * self._d - (self.kd / (self.tau_d + dt)) * (y - self._y_prev)
        self._y_prev = y

        u_unsat = self.kp * e + self._i + self._d
        u = min(max(u_unsat, self.u_min), self.u_max)

        # back-calculation só faz sentido quando há ação integral (ki != 0)
        windup_term = self.kb * (u - u_unsat) if (self.anti_windup and self.ki) else 0.0
        self._i += dt * (self.ki * e + windup_term)
        return u
