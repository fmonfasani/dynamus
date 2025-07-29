# src/genesis_agents/base/exceptions.py
"""
Excepciones específicas para agentes Genesis
"""


class AgentException(Exception):
    """Excepción base para agentes Genesis"""
    pass


class AgentInitializationError(AgentException):
    """Error durante inicialización del agente"""
    pass


class TaskExecutionError(AgentException):
    """Error durante ejecución de tarea"""
    pass


class CapabilityNotSupportedError(AgentException):
    """Capacidad no soportada por el agente"""
    pass


class AgentConfigurationError(AgentException):
    """Error de configuración del agente"""
    pass


class AgentRegistryError(AgentException):
    """Error en el registry de agentes"""
    pass


class AgentDiscoveryError(AgentException):
    """Error durante discovery de agentes"""
    pass


class TaskTimeoutError(TaskExecutionError):
    """Timeout en ejecución de tarea"""
    pass


class AgentOverloadError(AgentException):
    """Agente sobrecargado (demasiadas tareas)"""
    pass