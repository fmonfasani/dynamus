# src/genesis_agents/registry/discovery.py
"""
Auto-discovery de agentes en el ecosistema - Hub Independiente

MANDAMIENTOS:
✅ NO fuerza instalación de paquetes específicos
✅ Descubre graciosamente lo que está disponible
✅ Configurable y extensible
✅ Logging detallado para debugging
"""

import importlib
import importlib.util
from typing import List, Dict, Set, Optional
from pathlib import Path
import sys

from genesis_agents.base.exceptions import AgentDiscoveryError


class AgentDiscovery:
    """
    Descubrimiento automático de agentes del ecosistema - Hub Independiente
    
    RESPONSABILIDADES:
    - Descubrir módulos estándar del ecosistema
    - Descubrir agentes locales en paths específicos
    - Validar disponibilidad de módulos
    - Proveer estrategias de discovery configurables
    
    NO HACE:
    - Forzar instalación de módulos
    - Manejo de registro (eso es del registry)
    - Lógica de agentes específicos
    """
    
    @staticmethod
    def discover_ecosystem_agents() -> List[str]:
        """
        Descubrir agentes del ecosistema Genesis estándar
        
        INDEPENDENCIA: Solo retorna módulos que están REALMENTE instalados
        """
        # Módulos estándar del ecosistema Genesis
        standard_modules = [
            # Agentes especializados por dominio
            "genesis_backend.agents",
            "genesis_frontend.agents", 
            "genesis_devops.agents",
            "genesis_ai.agents",
            
            # Agentes de templates y utils
            "genesis_templates.agents",
            "genesis_utils.agents",
            
            # Agentes de performance y testing
            "genesis_performance.agents",
            "genesis_testing.agents",
            
            # Agentes built-in del hub
            "genesis_agents.builtin",
        ]
        
        available_modules = []
        
        import logging
        logger = logging.getLogger("genesis.discovery")
        
        for module_name in standard_modules:
            try:
                # INDEPENDENCIA: Intentar importar sin forzar
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    # Módulo existe, intentar importar
                    importlib.import_module(module_name)
                    available_modules.append(module_name)
                    logger.debug(f"[OK] Found ecosystem module: {module_name}")
                else:
                    logger.debug(f"[SKIP] Module not installed: {module_name}")
                    
            except ImportError as e:
                # Módulo no disponible o tiene errores de importación
                logger.debug(f"[SKIP] Module {module_name} import failed: {e}")
            except Exception as e:
                # Error inesperado
                logger.warning(f"[WARN] Unexpected error with module {module_name}: {e}")
        
        logger.info(f"[DISCOVERY] Found {len(available_modules)} ecosystem modules: {available_modules}")
        return available_modules
    
    @staticmethod
    def discover_local_agents(search_paths: List[Path]) -> List[str]:
        """
        Descubrir agentes locales en paths específicos
        
        Útil para desarrollo local o instalaciones personalizadas
        """
        discovered = []
        
        import logging
        logger = logging.getLogger("genesis.discovery")
        
        for path in search_paths:
            if not path.exists() or not path.is_dir():
                logger.debug(f"[SKIP] Path does not exist: {path}")
                continue
            
            try:
                # Buscar archivos Python que puedan contener agentes
                agent_files = list(path.glob("**/*_agent.py"))
                
                for py_file in agent_files:
                    if py_file.is_file():
                        try:
                            # Convertir path a nombre de módulo
                            relative_path = py_file.relative_to(path.parent)
                            module_name = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
                            
                            # Verificar que el módulo se puede importar
                            spec = importlib.util.spec_from_file_location(module_name, py_file)
                            if spec and spec.loader:
                                discovered.append(module_name)
                                logger.debug(f"[OK] Found local agent module: {module_name}")
                                
                        except Exception as e:
                            logger.debug(f"[SKIP] Failed to process {py_file}: {e}")
            
            except Exception as e:
                logger.warning(f"[WARN] Error scanning path {path}: {e}")
        
        logger.info(f"[DISCOVERY] Found {len(discovered)} local agent modules")
        return discovered
    
    @staticmethod
    def discover_by_entry_points() -> List[str]:
        """
        Descubrir agentes usando entry points de setuptools
        
        Permite que otros paquetes registren sus agentes automáticamente
        """
        discovered = []
        
        try:
            import pkg_resources
            
            # Buscar entry points del grupo 'genesis_agents'
            for entry_point in pkg_resources.iter_entry_points('genesis_agents'):
                try:
                    module_name = entry_point.module_name
                    discovered.append(module_name)
                except Exception as e:
                    import logging
                    logger = logging.getLogger("genesis.discovery")
                    logger.debug(f"[SKIP] Failed to load entry point {entry_point}: {e}")
        
        except ImportError:
            # pkg_resources no disponible
            pass
        
        return discovered
    
    @staticmethod
    def discover_from_config(config_dict: Dict[str, Any]) -> List[str]:
        """
        Descubrir agentes desde configuración
        
        Permite configuración explícita de módulos de agentes
        """
        discovered = []
        
        # Módulos explícitamente configurados
        explicit_modules = config_dict.get("agent_modules", [])
        
        # Paths de búsqueda configurados
        search_paths = config_dict.get("search_paths", [])
        if search_paths:
            search_path_objects = [Path(p) for p in search_paths]
            discovered.extend(AgentDiscovery.discover_local_agents(search_path_objects))
        
        # Entry points habilitados
        if config_dict.get("use_entry_points", False):
            discovered.extend(AgentDiscovery.discover_by_entry_points())
        
        # Combinar con módulos explícitos
        discovered.extend(explicit_modules)
        
        # Remover duplicados manteniendo orden
        seen = set()
        unique_discovered = []
        for module in discovered:
            if module not in seen:
                seen.add(module)
                unique_discovered.append(module)
        
        return unique_discovered
    
    @staticmethod
    def validate_module_availability(module_names: List[str]) -> Dict[str, bool]:
        """
        Validar disponibilidad de una lista de módulos
        
        Útil para verificar dependencias antes de discovery
        """
        availability = {}
        
        for module_name in module_names:
            try:
                spec = importlib.util.find_spec(module_name)
                availability[module_name] = spec is not None
            except Exception:
                availability[module_name] = False
        
        return availability
    
    @staticmethod
    def get_module_info(module_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información detallada de un módulo
        
        Útil para debugging y logging
        """
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return None
            
            module = importlib.import_module(module_name)
            
            return {
                "name": module_name,
                "file": getattr(spec, "origin", None),
                "package": getattr(spec, "parent", None),
                "has_get_agents": hasattr(module, "get_agents"),
                "doc": getattr(module, "__doc__", None),
                "version": getattr(module, "__version__", None)
            }
            
        except Exception as e:
            return {
                "name": module_name,
                "error": str(e),
                "available": False
            }


class DiscoveryStrategy:
    """
    Estrategia configurable para discovery de agentes
    
    Permite diferentes enfoques de discovery según el entorno
    """
    
    def __init__(self, name: str):
        self.name = name
        self.enabled_methods: Set[str] = set()
        self.config: Dict[str, Any] = {}
    
    def enable_ecosystem_discovery(self):
        """Habilitar discovery del ecosistema estándar"""
        self.enabled_methods.add("ecosystem")
        return self
    
    def enable_local_discovery(self, search_paths: List[str]):
        """Habilitar discovery local con paths específicos"""
        self.enabled_methods.add("local")
        self.config["search_paths"] = search_paths
        return self
    
    def enable_entry_points_discovery(self):
        """Habilitar discovery via entry points"""
        self.enabled_methods.add("entry_points")
        return self
    
    def enable_config_discovery(self, config: Dict[str, Any]):
        """Habilitar discovery desde configuración"""
        self.enabled_methods.add("config")
        self.config.update(config)
        return self
    
    def discover(self) -> List[str]:
        """Ejecutar discovery usando métodos habilitados"""
        all_modules = []
        
        if "ecosystem" in self.enabled_methods:
            all_modules.extend(AgentDiscovery.discover_ecosystem_agents())
        
        if "local" in self.enabled_methods:
            search_paths = [Path(p) for p in self.config.get("search_paths", [])]
            all_modules.extend(AgentDiscovery.discover_local_agents(search_paths))
        
        if "entry_points" in self.enabled_methods:
            all_modules.extend(AgentDiscovery.discover_by_entry_points())
        
        if "config" in self.enabled_methods:
            all_modules.extend(AgentDiscovery.discover_from_config(self.config))
        
        # Remover duplicados
        return list(set(all_modules))


# Estrategias predefinidas
def create_default_strategy() -> DiscoveryStrategy:
    """Estrategia por defecto para la mayoría de casos"""
    return (DiscoveryStrategy("default")
            .enable_ecosystem_discovery()
            .enable_entry_points_discovery())


def create_development_strategy(project_root: str) -> DiscoveryStrategy:
    """Estrategia para desarrollo local"""
    return (DiscoveryStrategy("development")
            .enable_ecosystem_discovery()
            .enable_local_discovery([f"{project_root}/agents", f"{project_root}/custom_agents"])
            .enable_entry_points_discovery())


def create_production_strategy() -> DiscoveryStrategy:
    """Estrategia para producción (solo ecosistema estándar)"""
    return (DiscoveryStrategy("production")
            .enable_ecosystem_discovery())