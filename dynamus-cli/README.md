# ⚙️ dynamus-cli

**CLI del ecosistema Dynamus**

`dynamus-cli` es la piedra angular para construir agentes inteligentes y modulares dentro del ecosistema Dynamus. Diseñado con principios de extensibilidad, descubrimiento dinámico y sinergia entre componentes.

---

## 🧩 Artefacto

```text
📦 dynamus-cli
    ├── 🔧 cli.py
    ├── 📁 __init__.py
```

---

## 🚀 Instalación

```bash
pip install dynamus-cli
```

O bien instalá todo el ecosistema:

```bash
pip install dynamus
```

---

## 🔍 Funcionalidades principales

- Creación de agentes inteligentes con interfaz común.
- Registro y descubrimiento en tiempo de ejecución.
- Integración con `dynamus-cli` y protocolos MCP/CLI.
- Sistema de capacidades y especialización de agentes.

---

## 🧠 Ejemplo básico

```python
from dynamus_cli import DynamusCLI

class MyCLI(DynamusCLI):
    def run(self):
        print("Hola desde MyCLI!")

agent = MyCLI(name="test-cli")
agent.run()
```

---

## 📄 Licencia

MIT License — Federico Monfasani · [fmonfasani@gmail.com](mailto:fmonfasani@gmail.com)

---

## 🤝 Contribuciones

¡Pull requests bienvenidos! Este paquete forma parte del ecosistema [Dynamus](https://pypi.org/project/dynamus/).
