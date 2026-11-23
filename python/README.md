# Motor de referência em Python

Implementação em Python do mesmo modelo usado pelo VisualPID (`index.html`).
Serve para **validar a página contra a teoria**: os testes verificam, por exemplo,
que o erro em regime do controle P é `1/(1+Kp·K)` e que a integral elimina o erro
diante de perturbação. Os números do motor DC aqui batem com os da página.

```bash
cd python
pip install -r requirements.txt
pip install -e .
pytest -v
python examples/compare_tunings.py   # gera docs/compare_tunings.png
python examples/windup_demo.py       # gera docs/windup_demo.png
```

```python
from pidsim import PID, dc_motor, simulate, step_metrics

res = simulate(dc_motor(), PID(kp=100, ki=200, u_min=-12, u_max=12), setpoint=1.0, t_end=3)
print(step_metrics(res))
```
