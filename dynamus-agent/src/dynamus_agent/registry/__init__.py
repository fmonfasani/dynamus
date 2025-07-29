# src/genesis_agents/__init__.py
"""
Genesis Agents - Independent Hub for Genesis Engine Ecosystem

This package provides the foundational classes and registry for all Genesis agents.
It's designed to be completely independent - other packages depend on it, not the reverse.

Key Components:
- GenesisAgent: Base class for all agents
- AgentCapability: Enum of agent capabilities  
- GenesisAgentRegistry: Central registry with auto-discovery
- AgentDiscovery: Discovery strategies for ecosystem agents

Usage:
    from genesis_agents import GenesisAgent, AgentCapability
    from genesis_agents.registry import GenesisAgentRegistry
    
    # Create custom agent
    class MyAgent(GenesisAgent):
        def __init__(self):
            super().__init__(
                agent_id="my_agent",
                name="MyAgent", 
                agent_type="custom",
                capabilities=[AgentCapability.API_GENERATION]
            )
        
        async def _initialize_genesis_agent(self):
            # Custom initialization
            pass
        
        async def _execute_task_implementation(self, task):
            # Custom task execution
            return TaskResult(task_id=task.id, success=True)
"""

__version__ = "1.0.0"
__author__ = "Genesis Team"
__email__ = "team@genesis-engine.dev"

# Core exports
from genesis_agents.base.genesis_agent import (
    GenesisAgent,
    AgentTask,
    TaskResult,
    AgentStatus,
    AgentMetrics,
    ExampleGenesisAgent  # For testing/examples only
)

from genesis_agents.base.capabilities import (
    AgentCapability,
    CapabilityCategory,
    get_capabilities_by_category,
    get_capability_category,
    validate_capability_combination,
    COMMON_AGENT_CAPABILITIES
)

from genesis_agents.base.exceptions import (
    AgentException,
    AgentInitializationError,
    TaskExecutionError,
    CapabilityNotSupportedError,
    AgentConfigurationError,
    AgentRegistryError,
    AgentDiscoveryError,
    TaskTimeoutError,
    AgentOverloadError
)

# Registry exports
from genesis_agents.registry.agent_registry import GenesisAgentRegistry
from genesis_agents.registry.discovery import (
    AgentDiscovery,
    DiscoveryStrategy,
    create_default_strategy,
    create_development_strategy,
    create_production_strategy
)

# Communication exports
try:
    from genesis_agents.communication.mcp_bridge import MCPBridge
except ImportError:
    # MCPBridge might depend on additional packages
    MCPBridge = None

__all__ = [
    # Core classes
    "GenesisAgent",
    "AgentTask", 
    "TaskResult",
    "AgentStatus",
    "AgentMetrics",
    
    # Capabilities
    "AgentCapability",
    "CapabilityCategory",
    "get_capabilities_by_category",
    "get_capability_category", 
    "validate_capability_combination",
    "COMMON_AGENT_CAPABILITIES",
    
    # Exceptions
    "AgentException",
    "AgentInitializationError",
    "TaskExecutionError",
    "CapabilityNotSupportedError",
    "AgentConfigurationError",
    "AgentRegistryError",
    "AgentDiscoveryError",
    "TaskTimeoutError",
    "AgentOverloadError",
    
    # Registry
    "GenesisAgentRegistry",
    "AgentDiscovery",
    "DiscoveryStrategy",
    "create_default_strategy",
    "create_development_strategy",
    "create_production_strategy",
    
    # Communication
    "MCPBridge",
    
    # Example (for testing)
    "ExampleGenesisAgent",
]

# Package metadata
__package_name__ = "genesis-agents"
__package_description__ = "Independent hub for Genesis Engine agent ecosystem"
__package_url__ = "https://github.com/genesis-engine/genesis-agents"
__package_license__ = "MIT"