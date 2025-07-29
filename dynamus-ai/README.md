# ⚙️ dynamus-ai

**AI del ecosistema Dynamus**

`dynamus-ai` es la piedra angular para construir agentes inteligentes y modulares dentro del ecosistema Dynamus. Diseñado con principios de extensibilidad, descubrimiento dinámico y sinergia entre componentes.

---

## 🧩 Artefacto

```text
📦 dynamus-ai
    ├── 🔧 ai.py
    ├── 📁 __init__.py
```

---

## 🚀 Instalación

```bash
pip install dynamus-ai
```

O bien instalá todo el ecosistema:

```bash
pip install dynamus
```

---

## 🔍 Funcionalidades principales

- Creación de agentes inteligentes con interfaz común.
- Registro y descubrimiento en tiempo de ejecución.
- Integración con `dynamus-ai` y protocolos MCP/CLI.
- Sistema de capacidades y especialización de agentes.

---

## 🧠 Ejemplo básico

```python
from dynamus_ai import DynamusAI

class MyAI(DynamusAI):
    def run(self):
        print("Hola desde MyAI!")

agent = MyAI(name="test-ai")
agent.run()
```

---

## 📄 Licencia

MIT License — Federico Monfasani · [fmonfasani@gmail.com](mailto:fmonfasani@gmail.com)

---

## 🤝 Contribuciones

¡Pull requests bienvenidos! Este paquete forma parte del ecosistema [Dynamus](https://pypi.org/project/dynamus/).
