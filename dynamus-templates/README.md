# ⚙️ dynamus-templates

**Templates del ecosistema Dynamus**

`dynamus-templates` es la piedra angular para construir agentes inteligentes y modulares dentro del ecosistema Dynamus. Diseñado con principios de extensibilidad, descubrimiento dinámico y sinergia entre componentes.

---

## 🧩 Artefacto

```text
📦 dynamus-templates
    ├── 🔧 templates.py
    ├── 📁 __init__.py
```

---

## 🚀 Instalación

```bash
pip install dynamus-templates
```

O bien instalá todo el ecosistema:

```bash
pip install dynamus
```

---

## 🔍 Funcionalidades principales

- Creación de agentes inteligentes con interfaz común.
- Registro y descubrimiento en tiempo de ejecución.
- Integración con `dynamus-templates` y protocolos MCP/CLI.
- Sistema de capacidades y especialización de agentes.

---

## 🧠 Ejemplo básico

```python
from dynamus_templates import DynamusTemplates

class MyTemplates(DynamusTemplates):
    def run(self):
        print("Hola desde MyTemplates!")

agent = MyTemplates(name="test-templates")
agent.run()
```

---

## 📄 Licencia

MIT License — Federico Monfasani · [fmonfasani@gmail.com](mailto:fmonfasani@gmail.com)

---

## 🤝 Contribuciones

¡Pull requests bienvenidos! Este paquete forma parte del ecosistema [Dynamus](https://pypi.org/project/dynamus/).
