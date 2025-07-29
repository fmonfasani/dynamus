# ⚙️ dynamus-frontend

**Frontend del ecosistema Dynamus**

`dynamus-frontend` es la piedra angular para construir agentes inteligentes y modulares dentro del ecosistema Dynamus. Diseñado con principios de extensibilidad, descubrimiento dinámico y sinergia entre componentes.

---

## 🧩 Artefacto

```text
📦 dynamus-frontend
    ├── 🔧 frontend.py
    ├── 📁 __init__.py
```

---

## 🚀 Instalación

```bash
pip install dynamus-frontend
```

O bien instalá todo el ecosistema:

```bash
pip install dynamus
```

---

## 🔍 Funcionalidades principales

- Creación de agentes inteligentes con interfaz común.
- Registro y descubrimiento en tiempo de ejecución.
- Integración con `dynamus-frontend` y protocolos MCP/CLI.
- Sistema de capacidades y especialización de agentes.

---

## 🧠 Ejemplo básico

```python
from dynamus_frontend import DynamusFrontend

class MyFrontend(DynamusFrontend):
    def run(self):
        print("Hola desde MyFrontend!")

agent = MyFrontend(name="test-frontend")
agent.run()
```

---

## 📄 Licencia

MIT License — Federico Monfasani · [fmonfasani@gmail.com](mailto:fmonfasani@gmail.com)

---

## 🤝 Contribuciones

¡Pull requests bienvenidos! Este paquete forma parte del ecosistema [Dynamus](https://pypi.org/project/dynamus/).
