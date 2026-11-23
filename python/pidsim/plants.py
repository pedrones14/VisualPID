"""Plantas lineares (espaço de estados) discretizadas por ZOH."""
from __future__ import annotations

import numpy as np
from scipy.signal import cont2discrete


class StateSpacePlant:
    """Planta SISO  x' = A x + B u,  y = C x  (D = 0), simulada em tempo discreto."""

    def __init__(self, A, B, C, dt: float = 1e-3, name: str = "planta"):
        self.A = np.atleast_2d(np.asarray(A, dtype=float))
        self.B = np.asarray(B, dtype=float).reshape(-1, 1)
        self.C = np.asarray(C, dtype=float).reshape(1, -1)
        self.dt = float(dt)
        self.name = name
        Ad, Bd, _, _, _ = cont2discrete(
            (self.A, self.B, self.C, np.zeros((1, 1))), self.dt, method="zoh"
        )
        self._Ad, self._Bd = Ad, Bd
        self.reset()

    def reset(self, x0=None) -> None:
        n = self.A.shape[0]
        self.x = np.zeros((n, 1)) if x0 is None else np.asarray(x0, float).reshape(n, 1)

    def output(self) -> float:
        return float((self.C @ self.x).item())

    def step(self, u: float) -> float:
        """Avança um passo de tempo com entrada u e devolve a nova saída."""
        self.x = self._Ad @ self.x + self._Bd * float(u)
        return self.output()

    def dc_gain(self) -> float:
        return float((-self.C @ np.linalg.solve(self.A, self.B)).item())


def first_order(K: float = 1.0, tau: float = 1.0, dt: float = 1e-3) -> StateSpacePlant:
    """G(s) = K / (tau s + 1)  (ex.: nível de tanque, temperatura)."""
    return StateSpacePlant([[-1 / tau]], [K / tau], [1.0], dt, "1ª ordem")


def dc_motor(J=0.01, b=0.1, K=0.01, R=1.0, L=0.5, dt: float = 1e-3) -> StateSpacePlant:
    """Motor DC: entrada = tensão (V), saída = velocidade angular (rad/s).

    Estados: [omega, corrente].  Parâmetros do clássico exemplo da CTMS (Michigan).
    """
    A = [[-b / J, K / J], [-K / L, -R / L]]
    B = [0.0, 1 / L]
    C = [1.0, 0.0]
    return StateSpacePlant(A, B, C, dt, "Motor DC")


def mass_spring_damper(m=1.0, c=0.5, k=2.0, dt: float = 1e-3) -> StateSpacePlant:
    """Massa-mola-amortecedor: entrada = força (N), saída = posição (m)."""
    A = [[0.0, 1.0], [-k / m, -c / m]]
    B = [0.0, 1 / m]
    C = [1.0, 0.0]
    return StateSpacePlant(A, B, C, dt, "Massa-mola-amortecedor")
