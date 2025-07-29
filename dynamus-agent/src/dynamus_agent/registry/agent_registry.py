# src/genesis_agents/registry/agent_registry.py
"""
Registry central de agentes con auto-discovery - Hub Independiente

MANDAMIENTOS DEL HUB:
✅ NO depende de paquetes específicos (genesis-backend, etc.)
✅ Auto-discovery gracioso (no falla si no están instalados)
✅ Integración con MCPturbo registry
✅ Mapeo de capacidades a agentes
"""

import importlib
import inspect
from typing import Dict, List, Optional, Type, Any, Set
from pathlib import Path

# DEPENDENCIA: Solo MCPturbo (hub independiente)
from mcpturbo.agents import AgentRegistry as MCPAgentRegistry

from genesis_agents.base.genesis_agent import GenesisAgent
from genesis_agents.base.capabilities import AgentCapability, CapabilityCategory
from genesis_agents.base.exceptions import AgentRegistryError, AgentDiscoveryError


class GenesisAgentRegistry:
    """
    Registry central de agentes Genesis - Hub Independiente
    
    RESPONSABILIDADES:
    - Auto-discovery de agentes sin dependencias forzadas
    - Registro en MCPturbo registry
    - Mapeo de capacidades a agentes
    - Validación y estadísticas
    - Gestión de ciclo de vida de agentes
    
    NO HACE:
    - Forzar instalación de paquetes específicos
    - Implementar lógica de agentes específicos
    - Manejo de workflows (eso es del orchestrator)
    """
    
    def __init__(self, mcp_registry: Optional[MCPAgentRegistry] = None):
        # DEPENDENCIA: Integración con MCPturbo registry
        self.mcp_registry = mcp_registry
        
        # Registry interno de agentes Genesis
        self.agents: Dict[str, GenesisAgent] = {}
        self.agent_classes: Dict[str, Type[GenesisAgent]] = {}
        self.capabilities_map: Dict[AgentCapability, List[str]] = {}
        self.category_map: Dict[CapabilityCategory, List[str]] = {}
        
        # Discovery tracking
        self.discovered_modules: List[str] = []
        self.failed_modules: List[str] = []
        
        # Stats
        self.stats = {
            "total_agents": 0,
            "agents_by_type": {},
            "agents_by_category": {},
            "capabilities_coverage": {},
            "discovery_attempts": 0,
            "discovery_successes": 0
        }
        
        import logging
        self.logger = logging.getLogger("genesis.registry")
    
    def register_agent(self, agent: GenesisAgent):
        """
        Registrar agente individual
        
        INTEGRACIÓN: Registra tanto en registry interno como en MCPturbo
        """
        try:
            agent_id = agent.agent_id
            
            # Validar agente
            self._validate_agent(agent)
            
            # DEPENDENCIA: Registrar en MCPturbo registry si está disponible
            if self.mcp_registry:
                self.mcp_registry.register(agent)
            
            # Registrar en registry interno
            self.agents[agent_id] = agent
            self.agent_classes[agent_id] = type(agent)
            
            # Mapear capacidades
            self._map_agent_capabilities(agent)
            
            # Actualizar estadísticas
            self._update_stats_for_agent(agent, "add")
            
            self.logger.info(
                f"[OK] Registered agent: {agent.name} ({agent_id}) "
                f"with {len(agent.get_capabilities())} capabilities"
            )
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to register agent {agent.agent_id}: {e}")
            raise AgentRegistryError(f"Failed to register agent {agent.agent_id}: {e}")
    
    def unregister_agent(self, agent_id: str):
        """Desregistrar agente"""
        if agent_id not in self.agents:
            self.logger.warning(f"[WARN] Agent {agent_id} not found for unregistration")
            return
        
        try:
            agent = self.agents[agent_id]
            
            # DEPENDENCIA: Desregistrar de MCPturbo
            if self.mcp_registry:
                self.mcp_registry.unregister(agent_id)
            
            # Remover del registry interno
            del self.agents[agent_id]
            del self.agent_classes[agent_id]
            
            # Actualizar mapeos de capacidades
            self._unmap_agent_capabilities(agent)
            
            # Actualizar estadísticas
            self._update_stats_for_agent(agent, "remove")
            
            self.logger.info(f"[OK] Unregistered agent: {agent.name} ({agent_id})")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to unregister agent {agent_id}: {e}")
            raise AgentRegistryError(f"Failed to unregister agent {agent_id}: {e}")
    
    def discover_and_register_agents(self, module_names: List[str]):
        """
        Auto-discovery y registro de agentes desde módulos
        
        INDEPENDENCIA: No falla si módulos no están instalados
        """
        self.stats["discovery_attempts"] += len(module_names)
        
        for module_name in module_names:
            try:
                success = self._discover_module_agents(module_name)
                if success:
                    self.stats["discovery_successes"] += 1
                    
            except Exception as e:
                self.logger.warning(f"[WARN] Failed to discover agents from {module_name}: {e}")
                self.failed_modules.append(module_name)
        
        self.logger.info(
            f"[DISCOVERY] Completed discovery: "
            f"{self.stats['discovery_successes']}/{self.stats['discovery_attempts']} modules successful, "
            f"{len(self.agents)} total agents registered"
        )
    
    def _discover_module_agents(self, module_name: str) -> bool:
        """
        Descubrir agentes en un módulo específico
        
        INDEPENDENCIA: Retorna False si módulo no existe, no falla
        """
        try:
            # INDEPENDENCIA: Intentar importar sin forzar
            module = importlib.import_module(module_name)
            agents_found = 0
            
            # Buscar función get_agents (patrón preferido)
            if hasattr(module, 'get_agents'):
                agent_classes = module.get_agents()
                
                for agent_class in agent_classes:
                    if self._is_valid_agent_class(agent_class):
                        try:
                            # Instanciar y registrar
                            agent = agent_class()
                            self.register_agent(agent)
                            agents_found += 1
                        except Exception as e:
                            self.logger.warning(f"[WARN] Failed to instantiate {agent_class.__name__}: {e}")
            
            else:
                # Buscar clases de agentes directamente
                agent_classes = self._find_agent_classes_in_module(module)
                
                for agent_class in agent_classes:
                    try:
                        agent = agent_class()
                        self.register_agent(agent)
                        agents_found += 1
                    except Exception as e:
                        self.logger.warning(f"[WARN] Failed to instantiate {agent_class.__name__}: {e}")
            
            if agents_found > 0:
                self.discovered_modules.append(module_name)
                self.logger.info(f"[OK] Discovered {agents_found} agents from {module_name}")
                return True
            else:
                self.logger.debug(f"[DEBUG] No agents found in {module_name}")
                return False
                
        except ImportError:
            # INDEPENDENCIA: Módulo no instalado, continuar silenciosamente
            self.logger.debug(f"[DEBUG] Module {module_name} not available (not installed)")
            return False
        except Exception as e:
            self.logger.error(f"[ERROR] Error discovering agents from {module_name}: {e}")
            raise AgentDiscoveryError(f"Error discovering agents from {module_name}: {e}")
    
    def _find_agent_classes_in_module(self, module) -> List[Type[GenesisAgent]]:
        """Encontrar clases de agentes en un módulo"""
        agent_classes = []
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if self._is_valid_agent_class(obj):
                agent_classes.append(obj)
        
        return agent_classes
    
    def _is_valid_agent_class(self, agent_class: Type) -> bool:
        """Validar que una clase es un agente válido"""
        return (
            inspect.isclass(agent_class) and
            issubclass(agent_class, GenesisAgent) and
            agent_class != GenesisAgent and
            not agent_class.__name__.startswith('_') and
            not getattr(agent_class, '__abstract__', False)
        )
    
    def _validate_agent(self, agent: GenesisAgent):
        """Validar agente antes de registro"""
        if not agent.agent_id:
            raise AgentRegistryError("Agent must have an agent_id")
        
        if agent.agent_id in self.agents:
            raise AgentRegistryError(f"Agent {agent.agent_id} already registered")
        
        if not agent.get_capabilities():
            raise AgentRegistryError(f"Agent {agent.agent_id} must have at least one capability")
    
    def _map_agent_capabilities(self, agent: GenesisAgent):
        """Mapear capacidades del agente"""
        agent_id = agent.agent_id
        
        for capability in agent.get_capabilities():
            # Mapear por capacidad específica
            if capability not in self.capabilities_map:
                self.capabilities_map[capability] = []
            self.capabilities_map[capability].append(agent_id)
            
            # Mapear por categoría
            from genesis_agents.base.capabilities import get_capability_category
            category = get_capability_category(capability)
            if category not in self.category_map:
                self.category_map[category] = []
            if agent_id not in self.category_map[category]:
                self.category_map[category].append(agent_id)
    
    def _unmap_agent_capabilities(self, agent: GenesisAgent):
        """Desmapear capacidades del agente"""
        agent_id = agent.agent_id
        
        # Remover de capabilities_map
        for capability, agent_list in self.capabilities_map.items():
            if agent_id in agent_list:
                agent_list.remove(agent_id)
        
        # Remover de category_map
        for category, agent_list in self.category_map.items():
            if agent_id in agent_list:
                agent_list.remove(agent_id)
    
    def _update_stats_for_agent(self, agent: GenesisAgent, operation: str):
        """Actualizar estadísticas para agente"""
        if operation == "add":
            self.stats["total_agents"] += 1
            
            # Por tipo
            agent_type = agent.agent_type
            self.stats["agents_by_type"][agent_type] = self.stats["agents_by_type"].get(agent_type, 0) + 1
            
            # Por categorías
            from genesis_agents.base.capabilities import get_capability_category
            categories = set(get_capability_category(cap) for cap in agent.get_capabilities())
            for category in categories:
                cat_name = category.value
                self.stats["agents_by_category"][cat_name] = self.stats["agents_by_category"].get(cat_name, 0) + 1
            
            # Cobertura de capacidades
            for capability in agent.get_capabilities():
                cap_name = capability.value
                self.stats["capabilities_coverage"][cap_name] = self.stats["capabilities_coverage"].get(cap_name, 0) + 1
        
        elif operation == "remove":
            self.stats["total_agents"] -= 1
            # Recalcular otras estadísticas...
    
    # MÉTODOS DE CONSULTA PARA ORQUESTADORES
    
    def get_agent(self, agent_id: str) -> Optional[GenesisAgent]:
        """Obtener agente por ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[GenesisAgent]:
        """Obtener agentes por capacidad específica"""
        agent_ids = self.capabilities_map.get(capability, [])
        return [self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents]
    
    def get_agents_by_category(self, category: CapabilityCategory) -> List[GenesisAgent]:
        """Obtener agentes por categoría"""
        agent_ids = self.category_map.get(category, [])
        return [self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents]
    
    def get_agents_by_type(self, agent_type: str) -> List[GenesisAgent]:
        """Obtener agentes por tipo"""
        return [agent for agent in self.agents.values() if agent.agent_type == agent_type]
    
    def list_agents(self) -> List[str]:
        """Listar IDs de todos los agentes registrados"""
        return list(self.agents.keys())
    
    def list_available_capabilities(self) -> List[AgentCapability]:
        """Listar capacidades disponibles"""
        return list(self.capabilities_map.keys())
    
    def list_available_categories(self) -> List[CapabilityCategory]:
        """Listar categorías disponibles"""
        return list(self.category_map.keys())
    
    def get_capabilities_map(self) -> Dict[AgentCapability, List[str]]:
        """Obtener mapeo completo de capacidades a agentes"""
        return self.capabilities_map.copy()
    
    def get_category_map(self) -> Dict[CapabilityCategory, List[str]]:
        """Obtener mapeo completo de categorías a agentes"""
        return self.category_map.copy()
    
    def find_agents_for_task(self, required_capabilities: List[AgentCapability]) -> List[GenesisAgent]:
        """
        Encontrar agentes que pueden manejar un conjunto de capacidades
        
        Útil para el orchestrator cuando necesita encontrar agentes para tareas
        """
        suitable_agents = []
        
        for agent in self.agents.values():
            agent_capabilities = set(agent.get_capabilities())
            required_set = set(required_capabilities)
            
            # Verificar si el agente puede manejar TODAS las capacidades requeridas
            if required_set.issubset(agent_capabilities):
                suitable_agents.append(agent)
        
        return suitable_agents
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas completas del registry"""
        return {
            **self.stats,
            "discovered_modules": self.discovered_modules,
            "failed_modules": self.failed_modules,
            "capabilities_total": len(self.capabilities_map),
            "categories_covered": len(self.category_map),
            "active_agents": len([a for a in self.agents.values() if a.status.value == "ready"]),
            "mcp_integration": self.mcp_registry is not None
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check del registry y agentes"""
        healthy_agents = 0
        unhealthy_agents = 0
        
        agent_statuses = {}
        
        for agent_id, agent in self.agents.items():
            status = agent.status.value
            agent_statuses[agent_id] = status
            
            if status in ["ready", "busy"]:
                healthy_agents += 1
            else:
                unhealthy_agents += 1
        
        return {
            "registry_healthy": True,
            "total_agents": len(self.agents),
            "healthy_agents": healthy_agents,
            "unhealthy_agents": unhealthy_agents,
            "agent_statuses": agent_statuses,
            "mcp_connected": self.mcp_registry is not None,
            "discovery_success_rate": (
                self.stats["discovery_successes"] / max(self.stats["discovery_attempts"], 1) * 100
            )
        }