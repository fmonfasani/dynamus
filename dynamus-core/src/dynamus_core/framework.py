# ============================================
# dynamus/core/framework.py
# Framework base para generación de código
# ============================================

import os
import json
from typing import Dict, Any, List, Optional, Type, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
import importlib.util

@dataclass
class FieldDefinition:
    """Definición de un campo de entidad"""
    name: str
    type: str
    description: str = ""
    nullable: bool = True
    unique: bool = False
    index: bool = False
    primary_key: bool = False
    default: Any = None
    validation_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EntityDefinition:
    """Definición completa de una entidad"""
    name: str
    fields: List[FieldDefinition]
    table_name: Optional[str] = None
    description: str = ""
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationContext:
    """Contexto para generación de código"""
    entity: EntityDefinition
    framework: str = "fastapi"
    database: str = "postgresql"
    architecture: str = "layered"
    features: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    output_path: str = "./generated"

class CodeTemplate:
    """Representación de una plantilla de código"""
    
    def __init__(self, name: str, template_path: str, output_pattern: str, 
                 dependencies: List[str] = None):
        self.name = name
        self.template_path = template_path
        self.output_pattern = output_pattern
        self.dependencies = dependencies or []
        self._template: Optional[Template] = None
    
    def load_template(self, template_loader: Environment):
        """Carga la plantilla Jinja2"""
        self._template = template_loader.get_template(self.template_path)
    
    def render(self, context: Dict[str, Any]) -> str:
        """Renderiza la plantilla con el contexto dado"""
        if not self._template:
            raise ValueError(f"Template {self.name} not loaded")
        return self._template.render(**context)
    
    def get_output_path(self, context: GenerationContext) -> str:
        """Genera la ruta de salida basada en el patrón"""
        entity_name = context.entity.name.lower()
        return self.output_pattern.format(
            entity_name=entity_name,
            framework=context.framework,
            architecture=context.architecture
        )

class CodeGenerator(ABC):
    """Generador base de código"""
    
    @abstractmethod
    def generate(self, context: GenerationContext) -> Dict[str, str]:
        """Genera código basado en el contexto"""
        pass
    
    @abstractmethod
    def get_supported_frameworks(self) -> List[str]:
        """Retorna frameworks soportados"""
        pass
    
    @abstractmethod
    def get_dependencies(self, context: GenerationContext) -> List[str]:
        """Retorna dependencias necesarias"""
        pass

class TemplateBasedGenerator(CodeGenerator):
    """Generador basado en plantillas Jinja2"""
    
    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, CodeTemplate] = {}
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Agregar filtros personalizados
        self._setup_jinja_filters()
        
        # Cargar plantillas
        self._load_templates()
    
    def _setup_jinja_filters(self):
        """Configura filtros personalizados para Jinja2"""
        
        def to_snake_case(text: str) -> str:
            """Convierte a snake_case"""
            import re
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        def to_camel_case(text: str) -> str:
            """Convierte a camelCase"""
            components = text.split('_')
            return components[0] + ''.join(x.title() for x in components[1:])
        
        def to_pascal_case(text: str) -> str:
            """Convierte a PascalCase"""
            return ''.join(x.title() for x in text.split('_'))
        
        def pluralize(text: str) -> str:
            """Pluraliza una palabra (básico)"""
            if text.endswith('y'):
                return text[:-1] + 'ies'
            elif text.endswith(('s', 'sh', 'ch', 'x', 'z')):
                return text + 'es'
            else:
                return text + 's'
        
        def map_type_to_python(field_type: str) -> str:
            """Mapea tipos a Python/Pydantic"""
            type_mapping = {
                "string": "str",
                "text": "str",
                "integer": "int", 
                "float": "float",
                "boolean": "bool",
                "datetime": "datetime",
                "date": "date",
                "email": "EmailStr",
                "url": "HttpUrl",
                "uuid": "UUID"
            }
            return type_mapping.get(field_type.lower(), "str")
        
        def map_type_to_sqlalchemy(field_type: str) -> str:
            """Mapea tipos a SQLAlchemy"""
            type_mapping = {
                "string": "String(255)",
                "text": "Text",
                "integer": "Integer",
                "float": "Float", 
                "boolean": "Boolean",
                "datetime": "DateTime",
                "date": "Date",
                "email": "String(255)",
                "url": "String(255)",
                "uuid": "UUID(as_uuid=True)",
                "json": "JSON"
            }
            return type_mapping.get(field_type.lower(), "String(255)")
        
        # Registrar filtros
        self.jinja_env.filters['snake_case'] = to_snake_case
        self.jinja_env.filters['camel_case'] = to_camel_case
        self.jinja_env.filters['pascal_case'] = to_pascal_case
        self.jinja_env.filters['pluralize'] = pluralize
        self.jinja_env.filters['python_type'] = map_type_to_python
        self.jinja_env.filters['sqlalchemy_type'] = map_type_to_sqlalchemy
    
    def _load_templates(self):
        """Carga todas las plantillas del directorio"""
        # Buscar archivos .j2 en el directorio de plantillas
        for template_file in self.templates_dir.rglob("*.j2"):
            relative_path = template_file.relative_to(self.templates_dir)
            template_name = str(relative_path).replace('.j2', '')
            
            # Generar patrón de salida basado en la estructura
            output_pattern = self._generate_output_pattern(template_name)
            
            template = CodeTemplate(
                name=template_name,
                template_path=str(relative_path),
                output_pattern=output_pattern
            )
            
            template.load_template(self.jinja_env)
            self.templates[template_name] = template
    
    def _generate_output_pattern(self, template_name: str) -> str:
        """Genera patrón de salida para una plantilla"""
        # Mapear nombres de plantillas a rutas de salida
        pattern_mapping = {
            "fastapi/model": "app/models/{entity_name}.py",
            "fastapi/schema": "app/schemas/{entity_name}.py", 
            "fastapi/api": "app/api/{entity_name}.py",
            "fastapi/repository": "app/repositories/{entity_name}_repository.py",
            "fastapi/service": "app/services/{entity_name}_service.py",
            "fastapi/test": "tests/test_{entity_name}.py",
            "alembic/migration": "alembic/versions/create_{entity_name}.py",
            "docs/api": "docs/{entity_name}_api.md"
        }
        
        return pattern_mapping.get(template_name, f"generated/{template_name}")
    
    def generate(self, context: GenerationContext) -> Dict[str, str]:
        """Genera código basado en el contexto"""
        
        generated_files = {}
        
        # Preparar contexto para plantillas
        template_context = self._prepare_template_context(context)
        
        # Filtrar plantillas relevantes
        relevant_templates = self._get_relevant_templates(context)
        
        # Generar código para cada plantilla
        for template_name, template in relevant_templates.items():
            try:
                # Renderizar plantilla
                code = template.render(template_context)
                
                # Obtener ruta de salida
                output_path = template.get_output_path(context)
                
                generated_files[output_path] = code
                
            except Exception as e:
                raise RuntimeError(f"Error generando {template_name}: {e}")
        
        return generated_files
    
    def _prepare_template_context(self, context: GenerationContext) -> Dict[str, Any]:
        """Prepara el contexto para las plantillas"""
        
        entity = context.entity
        
        # Contexto base
        template_context = {
            "entity": entity,
            "entity_name": entity.name,
            "entity_name_lower": entity.name.lower(),
            "table_name": entity.table_name or f"{entity.name.lower()}s",
            "fields": entity.fields,
            "framework": context.framework,
            "database": context.database,
            "architecture": context.architecture,
            "features": context.features,
            "config": context.config
        }
        
        # Agregar utilidades
        template_context.update({
            "primary_key_field": self._get_primary_key_field(entity),
            "required_fields": [f for f in entity.fields if not f.nullable],
            "optional_fields": [f for f in entity.fields if f.nullable],
            "unique_fields": [f for f in entity.fields if f.unique],
            "indexed_fields": [f for f in entity.fields if f.index],
            "string_fields": [f for f in entity.fields if f.type == "string"],
            "numeric_fields": [f for f in entity.fields if f.type in ["integer", "float"]],
        })
        
        # Configuraciones específicas por feature
        if "auth" in context.features:
            template_context["include_auth"] = True
            template_context["auth_dependency"] = "get_current_user"
        
        if "pagination" in context.features:
            template_context["include_pagination"] = True
        
        if "soft_delete" in context.features:
            template_context["include_soft_delete"] = True
        
        return template_context