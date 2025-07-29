# src/genesis_agents/base/genesis_agent.py
"""
Clase base para todos los agentes Genesis - Hub Independiente

MANDAMIENTOS DEL HUB CUMPLIDOS:
✅ Hereda de MCPBaseAgent para compatibilidad total con MCPturbo
✅ Define interfaz estándar sin implementaciones específicas
✅ Manejo completo de ciclo de vida, métricas y logging
✅ NO depende de repos específicos (genesis-backend, etc.)
✅ Provee base extensible para todos los agentes del ecosistema

Este archivo es el fundamento de todo agente en el ecosistema Genesis.
Cada agente específico (BackendAgent, FrontendAgent, etc.) hereda de esta clase.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback
import inspect

# DEPENDENCIA: Solo MCPturbo (hub independiente)
try:
    from mcpturbo.agents import BaseAgent as MCPBaseAgent
    from mcpturbo.types import TaskPriority
    MCP_AVAILABLE = True
except ImportError:
    # Fallback si MCPturbo no está disponible (para testing)
    class MCPBaseAgent:
        def __init__(self, agent_id: str, capabilities: List[str]):
            self.agent_id = agent_id
            self.capabilities = capabilities
        
        async def start(self):
            pass
        
        async def stop(self):
            pass
    
    class TaskPriority(int, Enum):
        LOW = 1
        NORMAL = 2
        HIGH = 3
        CRITICAL = 4
    
    MCP_AVAILABLE = False

# Imports locales (se crearán después)
try:
    from genesis_agents.base.capabilities import AgentCapability
except ImportError:
    # Fallback temporal para desarrollo
    class AgentCapability(str, Enum):
        ARCHITECTURE_DESIGN = "architecture_design"
        API_GENERATION = "api_generation"

try:
    from genesis_agents.base.exceptions import (
        AgentException, 
        TaskExecutionError, 
        AgentInitializationError,
        TaskTimeoutError,
        AgentOverloadError,
        CapabilityNotSupportedError
    )
except ImportError:
    # Fallback temporal
    class AgentException(Exception):
        pass
    
    class TaskExecutionError(AgentException):
        pass
    
    class AgentInitializationError(AgentException):
        pass
    
    class TaskTimeoutError(TaskExecutionError):
        pass
    
    class AgentOverloadError(AgentException):
        pass
    
    class CapabilityNotSupportedError(AgentException):
        pass


class AgentStatus(str, Enum):
    """Estados del agente Genesis"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"


@dataclass
class AgentTask:
    """
    Tarea para agente Genesis
    
    Representa una unidad de trabajo que puede ejecutar un agente.
    Incluye toda la información necesaria para la ejecución y tracking.
    """
    id: str
    name: str
    description: str
    params: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: int = 300
    retry_attempts: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "params": self.params,
            "priority": self.priority.value if isinstance(self.priority, TaskPriority) else self.priority,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTask":
        """Crear desde diccionario"""
        data = data.copy()
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "priority" in data and isinstance(data["priority"], (int, str)):
            data["priority"] = TaskPriority(data["priority"])
        return cls(**data)


@dataclass
class TaskResult:
    """
    Resultado de ejecución de tarea
    
    Contiene toda la información sobre el resultado de una tarea,
    incluyendo éxito/fallo, datos generados, archivos creados, etc.
    """
    task_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_files: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    debug_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
            "generated_files": self.generated_files,
            "warnings": self.warnings,
            "debug_info": self.debug_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResult":
        """Crear desde diccionario"""
        return cls(**data)
    
    def add_warning(self, warning: str):
        """Agregar warning al resultado"""
        self.warnings.append(warning)
    
    def add_generated_file(self, file_path: str):
        """Agregar archivo generado"""
        if file_path not in self.generated_files:
            self.generated_files.append(file_path)
    
    def set_debug_info(self, key: str, value: Any):
        """Establecer información de debug"""
        self.debug_info[key] = value


@dataclass
class AgentMetrics:
    """
    Métricas del agente
    
    Tracking completo de performance y uso del agente
    """
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    last_activity: Optional[datetime] = None
    uptime: timedelta = field(default_factory=lambda: timedelta())
    error_rate: float = 0.0
    tasks_by_type: Dict[str, int] = field(default_factory=dict)
    performance_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_task_completion(self, task_name: str, execution_time: float, success: bool):
        """Actualizar métricas de tarea completada"""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        
        self.total_execution_time += execution_time
        total_tasks = self.tasks_completed + self.tasks_failed
        
        if total_tasks > 0:
            self.average_execution_time = self.total_execution_time / total_tasks
            self.error_rate = self.tasks_failed / total_tasks
        
        # Tracking por tipo de tarea
        self.tasks_by_type[task_name] = self.tasks_by_type.get(task_name, 0) + 1
        
        # Historial de performance (últimas 100 tareas)
        self.performance_history.append({
            "task_name": task_name,
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Mantener solo últimas 100 entradas
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        self.last_activity = datetime.utcnow()
    
    def get_success_rate(self) -> float:
        """Obtener tasa de éxito"""
        total = self.tasks_completed + self.tasks_failed
        return (self.tasks_completed / total * 100) if total > 0 else 0.0
    
    def get_recent_performance(self, minutes: int = 60) -> Dict[str, Any]:
        """Obtener performance reciente"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        recent_tasks = [
            task for task in self.performance_history
            if datetime.fromisoformat(task["timestamp"]) > cutoff
        ]
        
        if not recent_tasks:
            return {"tasks": 0, "avg_time": 0.0, "success_rate": 0.0}
        
        total_tasks = len(recent_tasks)
        successful_tasks = sum(1 for task in recent_tasks if task["success"])
        avg_time = sum(task["execution_time"] for task in recent_tasks) / total_tasks
        success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        return {
            "tasks": total_tasks,
            "avg_time": avg_time,
            "success_rate": success_rate,
            "timeframe_minutes": minutes
        }


class GenesisAgent(MCPBaseAgent, ABC):
    """
    Clase base para todos los agentes Genesis - Hub Independiente
    
    RESPONSABILIDADES:
    - Proporcionar interfaz estándar para agentes del ecosistema
    - Manejo completo de ciclo de vida (start/stop/restart)
    - Sistema de métricas y logging robusto
    - Integración transparente con MCPturbo
    - Validación de tareas y capacidades
    - Sistema de handlers de tareas extensible
    - Manejo de errores y timeouts
    - Health checking y monitoring
    
    NO HACE (mantiene independencia del hub):
    - Implementaciones específicas de generación de código
    - Comunicación directa con LLMs (eso es de MCPturbo)
    - Lógica de negocio específica (eso es de subclases)
    - Dependency injection de servicios específicos
    
    PATRÓN DE USO:
    
    class MyAgent(GenesisAgent):
        def __init__(self):
            super().__init__(
                agent_id="my_agent",
                name="MyAgent",
                agent_type="custom",
                capabilities=[AgentCapability.API_GENERATION]
            )
        
        async def _initialize_genesis_agent(self):
            # Inicialización específica
            self.register_task_handler("my_task", self._handle_my_task)
        
        async def _execute_task_implementation(self, task):
            # Lógica específica del agente
            return TaskResult(task_id=task.id, success=True)
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        capabilities: List[AgentCapability],
        version: str = "1.0.0",
        description: str = "",
        max_concurrent_tasks: int = 1,
        default_timeout: int = 300,
        auto_restart_on_error: bool = False
    ):
        """
        Inicializar agente Genesis
        
        Args:
            agent_id: ID único del agente
            name: Nombre descriptivo del agente
            agent_type: Tipo de agente (backend, frontend, devops, etc.)
            capabilities: Lista de capacidades que tiene el agente
            version: Versión del agente
            description: Descripción del agente
            max_concurrent_tasks: Máximo de tareas concurrentes
            default_timeout: Timeout por defecto para tareas
            auto_restart_on_error: Si reiniciar automáticamente en error
        """
        # DEPENDENCIA: Heredar de MCPBaseAgent para integración con MCPturbo
        if MCP_AVAILABLE:
            super().__init__(
                agent_id=agent_id,
                capabilities=[cap.value for cap in capabilities]
            )
        else:
            # Fallback para testing sin MCPturbo
            self.agent_id = agent_id
            self.capabilities = [cap.value for cap in capabilities]
        
        # Validación de parámetros
        if not agent_id or not agent_id.strip():
            raise AgentInitializationError("agent_id cannot be empty")
        if not name or not name.strip():
            raise AgentInitializationError("name cannot be empty")
        if not capabilities:
            raise AgentInitializationError("capabilities cannot be empty")
        
        # Propiedades Genesis específicas
        self.name = name
        self.agent_type = agent_type
        self.version = version
        self.description = description
        self.genesis_capabilities = capabilities
        
        # Configuración de ejecución
        self.max_concurrent_tasks = max(1, max_concurrent_tasks)
        self.default_timeout = max(10, default_timeout)  # Mínimo 10 segundos
        self.auto_restart_on_error = auto_restart_on_error
        
        # Estado del agente
        self.status = AgentStatus.INITIALIZING
        self.started_at: Optional[datetime] = None
        self.last_restart: Optional[datetime] = None
        self.restart_count: int = 0
        
        # Tareas y ejecución
        self.current_tasks: Dict[str, AgentTask] = {}
        self.task_history: List[AgentTask] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        
        # Métricas
        self.metrics = AgentMetrics()
        
        # Configuración dinámica
        self.config: Dict[str, Any] = {}
        
        # Logging
        import logging
        self.logger = logging.getLogger(f"genesis.agent.{agent_id}")
        
        # Sistema de handlers de tareas
        self._task_handlers: Dict[str, Callable] = {}
        self._middleware: List[Callable] = []
        
        # Control de shutdown graceful
        self._shutdown_event = asyncio.Event()
        self._shutdown_timeout = 30
        
        # Health checking
        self._last_health_check: Optional[datetime] = None
        self._health_check_interval = 60  # segundos
        
        self.logger.info(
            f"[INIT] Genesis Agent '{self.name}' ({agent_id}) initialized "
            f"with {len(capabilities)} capabilities"
        )
    
    # ============================================================================
    # CICLO DE VIDA DEL AGENTE
    # ============================================================================
    
    async def start(self):
        """
        Inicializar agente
        
        Secuencia de inicialización:
        1. Verificar estado actual
        2. Inicializar MCPBaseAgent 
        3. Ejecutar inicialización específica de Genesis
        4. Validar configuración
        5. Registrar handlers de tareas
        6. Marcar como READY
        """
        if self.status not in [AgentStatus.INITIALIZING, AgentStatus.STOPPED, AgentStatus.ERROR]:
            self.logger.warning(f"[WARN] Agent {self.name} already started (status: {self.status})")
            return
        
        try:
            self.logger.info(f"[START] Starting Genesis Agent {self.name}")
            self.status = AgentStatus.INITIALIZING
            
            # DEPENDENCIA: Inicialización de MCPBaseAgent
            if MCP_AVAILABLE:
                await super().start()
            
            # Inicialización específica de Genesis
            await self._initialize_genesis_agent()
            
            # Validar configuración del agente
            await self._validate_agent_configuration()
            
            # Registrar handlers de tareas
            self._register_task_handlers()
            
            # Inicializar middleware
            await self._initialize_middleware()
            
            # Marcar timestamps
            self.status = AgentStatus.READY
            self.started_at = datetime.utcnow()
            self._last_health_check = datetime.utcnow()
            
            # Reset shutdown event
            self._shutdown_event.clear()
            
            self.logger.info(f"[OK] Agent {self.name} started successfully")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"[ERROR] Failed to start agent {self.name}: {e}")
            self.logger.debug(f"[DEBUG] Start error traceback: {traceback.format_exc()}")
            raise AgentInitializationError(f"Failed to start agent {self.name}: {e}")
    
    async def stop(self):
        """
        Detener agente con shutdown graceful
        
        Secuencia de parada:
        1. Marcar shutdown event
        2. Cancelar tareas activas (con timeout)
        3. Cleanup de recursos específicos
        4. Detener MCPBaseAgent
        5. Marcar como STOPPED
        """
        if self.status == AgentStatus.STOPPED:
            return
        
        try:
            self.logger.info(f"[STOP] Stopping agent {self.name}")
            
            # Marcar shutdown
            self._shutdown_event.set()
            
            # Cancelar tareas activas con timeout
            await self._shutdown_tasks_gracefully()
            
            # Cleanup específico del agente
            await self._cleanup_agent_resources()
            
            # DEPENDENCIA: Detención de MCPBaseAgent
            if MCP_AVAILABLE:
                await super().stop()
            
            self.status = AgentStatus.STOPPED
            
            # Calcular uptime
            if self.started_at:
                self.metrics.uptime = datetime.utcnow() - self.started_at
            
            self.logger.info(
                f"[OK] Agent {self.name} stopped gracefully "
                f"(uptime: {self.metrics.uptime}, tasks completed: {self.metrics.tasks_completed})"
            )
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error stopping agent {self.name}: {e}")
            self.status = AgentStatus.ERROR
    
    async def restart(self):
        """
        Reiniciar agente
        
        Útil para recuperación de errores o reconfiguración
        """
        self.logger.info(f"[RESTART] Restarting agent {self.name}")
        
        try:
            await self.stop()
            await asyncio.sleep(1)  # Pausa breve
            await self.start()
            
            self.restart_count += 1
            self.last_restart = datetime.utcnow()
            
            self.logger.info(f"[OK] Agent {self.name} restarted successfully (restart #{self.restart_count})")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to restart agent {self.name}: {e}")
            self.status = AgentStatus.ERROR
            raise
    
    # ============================================================================
    # EJECUCIÓN DE TAREAS - INTERFAZ PRINCIPAL
    # ============================================================================
    
    async def execute_task(self, task: AgentTask) -> TaskResult:
        """
        Ejecutar tarea principal - INTERFAZ ESTÁNDAR
        
        Esta es la interfaz que usa MCPturbo y otros orquestadores.
        Incluye validación completa, manejo de timeouts, métricas y logging.
        
        Args:
            task: Tarea a ejecutar
            
        Returns:
            TaskResult con el resultado de la ejecución
        """
        # Validaciones previas
        if self.status != AgentStatus.READY:
            return TaskResult(
                task_id=task.id,
                success=False,
                error=f"Agent not ready (status: {self.status})"
            )
        
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            return TaskResult(
                task_id=task.id,
                success=False,
                error=f"Agent at max capacity ({self.max_concurrent_tasks} concurrent tasks)"
            )
        
        # Preparar ejecución
        start_time = datetime.utcnow()
        self.status = AgentStatus.BUSY
        self.current_tasks[task.id] = task
        
        try:
            self.logger.info(
                f"[EXEC] Starting task '{task.name}' (id: {task.id[:8]}...) "
                f"[{len(self.current_tasks)}/{self.max_concurrent_tasks}]"
            )
            
            # Validar que el agente puede manejar la tarea
            if not self._can_handle_task(task):
                raise CapabilityNotSupportedError(f"Agent cannot handle task: {task.name}")
            
            # Ejecutar middleware de pre-processing
            task = await self._execute_middleware(task, "pre")
            
            # Ejecutar tarea con timeout
            timeout = task.timeout if task.timeout > 0 else self.default_timeout
            result = await asyncio.wait_for(
                self._execute_task_with_retries(task),
                timeout=timeout
            )
            
            # Ejecutar middleware de post-processing
            result = await self._execute_middleware_post(task, result)
            
            # Calcular tiempo de ejecución
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time = execution_time
            
            # Actualizar métricas
            self.metrics.update_task_completion(task.name, execution_time, result.success)
            
            # Logging del resultado
            if result.success:
                self.logger.info(
                    f"[OK] Task '{task.name}' completed in {execution_time:.2f}s"
                )
                if result.generated_files:
                    self.logger.info(f"[FILES] Generated {len(result.generated_files)} files")
                if result.warnings:
                    self.logger.warning(f"[WARNINGS] {len(result.warnings)} warnings: {result.warnings}")
            else:
                self.logger.error(f"[ERROR] Task '{task.name}' failed: {result.error}")
            
            return result
            
        except asyncio.TimeoutError:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update_task_completion(task.name, execution_time, False)
            
            self.logger.error(f"[TIMEOUT] Task '{task.name}' timed out after {timeout}s")
            return TaskResult(
                task_id=task.id,
                success=False,
                error=f"Task timed out after {timeout} seconds",
                execution_time=execution_time
            )
            
        except CapabilityNotSupportedError as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update_task_completion(task.name, execution_time, False)
            
            self.logger.error(f"[CAPABILITY] {e}")
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update_task_completion(task.name, execution_time, False)
            
            self.logger.error(f"[ERROR] Task '{task.name}' execution failed: {e}")
            self.logger.debug(f"[DEBUG] Task error traceback: {traceback.format_exc()}")
            
            # Auto-restart en error crítico si está habilitado
            if self.auto_restart_on_error and isinstance(e, (AgentException, RuntimeError)):
                self.logger.warning(f"[AUTO-RESTART] Scheduling restart due to error")
                asyncio.create_task(self._schedule_restart())
            
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time=execution_time,
                debug_info={"traceback": traceback.format_exc()}
            )
        
        finally:
            # Cleanup
            self.current_tasks.pop(task.id, None)
            self.task_history.append(task)
            
            # Mantener historial limitado
            if len(self.task_history) > 100:
                self.task_history = self.task_history[-50:]
            
            # Volver a READY si no hay más tareas
            if not self.current_tasks:
                self.status = AgentStatus.READY
    
    async def _execute_task_with_retries(self, task: AgentTask) -> TaskResult:
        """Ejecutar tarea con sistema de reintentos"""
        last_error = None
        
        for attempt in range(task.retry_attempts):
            try:
                if attempt > 0:
                    self.logger.info(f"[RETRY] Attempt {attempt + 1}/{task.retry_attempts} for task {task.name}")
                    # Delay exponencial entre reintentos
                    await asyncio.sleep(min(2 ** attempt, 10))
                
                # DELEGACIÓN: Ejecutar implementación específica del agente
                result = await self._execute_task_implementation(task)
                
                # Si es exitoso, retornar inmediatamente
                if result.success:
                    if attempt > 0:
                        result.metadata["retries_used"] = attempt
                    return result
                
                # Si falló pero no es el último intento, continuar
                last_error = result.error
                if attempt < task.retry_attempts - 1:
                    self.logger.warning(f"[RETRY] Task {task.name} failed, retrying: {result.error}")
                    continue
                else:
                    # Último intento fallido
                    result.metadata["retries_exhausted"] = True
                    return result
                    
            except Exception as e:
                last_error = str(e)
                if attempt < task.retry_attempts - 1:
                    self.logger.warning(f"[RETRY] Task {task.name} raised exception, retrying: {e}")
                    continue
                else:
                    # Último intento con excepción
                    raise
        
        # No debería llegar aquí, pero por seguridad
        return TaskResult(
            task_id=task.id,
            success=False,
            error=f"All {task.retry_attempts} attempts failed. Last error: {last_error}"
        )
    
    # ============================================================================
    # MÉTODOS ABSTRACTOS - DEBEN SER IMPLEMENTADOS POR SUBCLASES
    # ============================================================================
    
    @abstractmethod
    async def _initialize_genesis_agent(self):
        """
        Inicialización específica del agente
        
        Cada agente debe implementar su lógica de inicialización específica.
        Típicamente incluye:
        - Registrar handlers de tareas
        - Configurar servicios específicos
        - Validar dependencias
        - Cargar configuración específica
        
        Ejemplo:
            async def _initialize_genesis_agent(self):
                self.register_task_handler("generate_api", self._handle_generate_api)
                self.register_task_handler("create_model", self._handle_create_model)
                self.set_config("framework", "fastapi")
        """
        pass
    
    @abstractmethod
    async def _execute_task_implementation(self, task: AgentTask) -> TaskResult:
        """
        Implementación específica de ejecución de tarea
        
        Cada agente debe implementar su lógica de ejecución específica.
        Esta función recibe una tarea validada y debe retornar un TaskResult.
        
        Args:
            task: Tarea validada lista para ejecutar
            
        Returns:
            TaskResult con el resultado de la ejecución
            
        Ejemplo:
            async def _execute_task_implementation(self, task: AgentTask) -> TaskResult:
                handler = self._task_handlers.get(task.name)
                if handler:
                    return await handler(task)
                
                return TaskResult(
                    task_id=task.id,
                    success=False,
                    error=f"No handler for task: {task.name}"
                )
        """
        pass
    
    # ============================================================================
    # MÉTODOS OPCIONALES - PUEDEN SER OVERRIDE POR SUBCLASES
    # ============================================================================
    
    async def _validate_agent_configuration(self):
        """
        Validar configuración del agente
        
        Implementación base que valida requisitos mínimos.
        Las subclases pueden override para validaciones específicas.
        """
        if not self.genesis_capabilities:
            raise AgentInitializationError("Agent must have at least one capability")
        
        if self.max_concurrent_tasks < 1:
            raise AgentInitializationError("max_concurrent_tasks must be >= 1")
        
        if self.default_timeout < 10:
            raise AgentInitializationError("default_timeout must be >= 10 seconds")
    
    async def _cleanup_agent_resources(self):
        """
        Cleanup de recursos específicos del agente
        
        Implementación base (vacía). Las subclases pueden override
        para cleanup específico como cerrar conexiones, liberar recursos, etc.
        """
        pass
    
    def _can_handle_task(self, task: AgentTask) -> bool:
        """
        Verificar si el agente puede manejar la tarea
        
        Implementación base que verifica si hay handler registrado.
        Las subclases pueden override para lógica más compleja.
        """
        return task.name in self._task_handlers
    
    def _register_task_handlers(self):
        """
        Registrar handlers de tareas
        
        Implementación base (vacía). Las subclases deben override
        para registrar sus handlers específicos.
        
        Ejemplo:
            def _register_task_handlers(self):
                self.register_task_handler("generate_api", self._handle_generate_api)
                self.register_task_handler("create_model", self._handle_create_model)
        """
        pass
    
    # ============================================================================
    # SISTEMA DE HANDLERS Y MIDDLEWARE
    # ============================================================================
    
    def register_task_handler(self, task_name: str, handler: Callable):
        """
        Registrar handler para tipo de tarea
        
        Args:
            task_name: Nombre de la tarea
            handler: Función async que maneja la tarea
        """
        if not asyncio.iscoroutinefunction(handler):
            raise AgentConfigurationError(f"Handler for {task_name} must be async")
        
        self._task_handlers[task_name] = handler
        self.logger.debug(f"[HANDLER] Registered handler for task: {task_name}")
    
    def unregister_task_handler(self, task_name: str):
        """Desregistrar handler de tarea"""
        if task_name in self._task_handlers:
            del self._task_handlers[task_name]
            self.logger.debug(f"[HANDLER] Unregistered handler for task: {task_name}")
    
    def register_middleware(self, middleware: Callable):
        """
        Registrar middleware para procesamiento de tareas
        
        El middleware se ejecuta antes y después de cada tarea.
        """
        if not asyncio.iscoroutinefunction(middleware):
            raise AgentConfigurationError("Middleware must be async")
        
        self._middleware.append(middleware)
        self.logger.debug(f"[MIDDLEWARE] Registered middleware: {middleware.__name__}")
    
    async def _execute_middleware(self, task: AgentTask, phase: str) -> AgentTask:
        """Ejecutar middleware de pre-processing"""
        for middleware in self._middleware:
            try:
                task = await middleware(task, phase, self)
            except Exception as e:
                self.logger.warning(f"[MIDDLEWARE] Middleware {middleware.__name__} failed: {e}")
        
        return task
    
    async def _execute_middleware_post(self, task: AgentTask, result: TaskResult) -> TaskResult:
        """Ejecutar middleware de post-processing"""
        for middleware in self._middleware:
            try:
                result = await middleware(task, "post", self, result)
            except Exception as e:
                self.logger.warning(f"[MIDDLEWARE] Post-middleware {middleware.__name__} failed: {e}")
        
        return result
    
    async def _initialize_middleware(self):
        """Inicializar middleware del agente"""
        # Implementación base - las subclases pueden override
        pass
    
    # ============================================================================
    # GESTIÓN DE CONFIGURACIÓN
    # ============================================================================
    
    def set_config(self, key: str, value: Any):
        """Establecer valor de configuración"""
        self.config[key] = value
        self.logger.debug(f"[CONFIG] Set {key} = {value}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        return self.config.get(key, default)
    
    def update_config(self, config_dict: Dict[str, Any]):
        """Actualizar múltiples valores de configuración"""
        self.config.update(config_dict)
        self.logger.debug(f"[CONFIG] Updated {len(config_dict)} config values")
    
    def clear_config(self):
        """Limpiar toda la configuración"""
        self.config.clear()
        self.logger.debug("[CONFIG] Cleared all config")
    
    # ============================================================================
    # MÉTODOS DE CONSULTA PARA ORQUESTADORES
    # ============================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado completo del agente"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.genesis_capabilities],
            "current_tasks": len(self.current_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "task_handlers": list(self._task_handlers.keys()),
            "middleware_count": len(self._middleware),
            "config_keys": list(self.config.keys()),
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "average_execution_time": self.metrics.average_execution_time,
                "error_rate": self.metrics.error_rate,
                "success_rate": self.metrics.get_success_rate(),
                "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None,
                "uptime": str(self.metrics.uptime),
                "tasks_by_type": self.metrics.tasks_by_type
            },
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "restart_count": self.restart_count,
            "last_restart": self.last_restart.isoformat() if self.last_restart else None,
            "mcp_integration": MCP_AVAILABLE
        }
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Obtener capacidades del agente"""
        return self.genesis_capabilities
    
    def can_handle_capability(self, capability: AgentCapability) -> bool:
        """Verificar si el agente puede manejar una capacidad"""
        return capability in self.genesis_capabilities
    
    def get_metrics(self) -> AgentMetrics:
        """Obtener métricas del agente"""
        return self.metrics
    
    def get_task_handlers(self) -> List[str]:
        """Obtener lista de handlers de tareas registrados"""
        return list(self._task_handlers.keys())
    
    def get_current_tasks(self) -> List[AgentTask]:
        """Obtener tareas actualmente en ejecución"""
        return list(self.current_tasks.values())
    
    def get_recent_tasks(self, limit: int = 10) -> List[AgentTask]:
        """Obtener tareas recientes del historial"""
        return self.task_history[-limit:] if self.task_history else []
    
    # ============================================================================
    # HEALTH CHECKING Y MONITORING
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check completo del agente
        
        Returns:
            Dict con estado de salud del agente
        """
        now = datetime.utcnow()
        self._last_health_check = now
        
        # Verificar estado básico
        is_healthy = self.status in [AgentStatus.READY, AgentStatus.BUSY]
        
        # Verificar última actividad
        time_since_activity = None
        if self.metrics.last_activity:
            time_since_activity = (now - self.metrics.last_activity).total_seconds()
        
        # Verificar performance reciente
        recent_perf = self.metrics.get_recent_performance(minutes=15)
        performance_ok = recent_perf["success_rate"] >= 70  # 70% success rate mínimo
        
        # Verificar carga
        load_percentage = (len(self.current_tasks) / self.max_concurrent_tasks) * 100
        load_ok = load_percentage < 90  # No más del 90% de carga
        
        overall_healthy = is_healthy and performance_ok and load_ok
        
        return {
            "healthy": overall_healthy,
            "status": self.status.value,
            "checks": {
                "status_ok": is_healthy,
                "performance_ok": performance_ok,
                "load_ok": load_ok
            },
            "details": {
                "uptime_seconds": (now - self.started_at).total_seconds() if self.started_at else 0,
                "time_since_last_activity": time_since_activity,
                "current_load_percentage": load_percentage,
                "recent_performance": recent_perf,
                "restart_count": self.restart_count,
                "error_rate": self.metrics.error_rate
            },
            "timestamp": now.isoformat()
        }
    
    # ============================================================================
    # MÉTODOS INTERNOS DE GESTIÓN
    # ============================================================================
    
    async def _shutdown_tasks_gracefully(self):
        """Shutdown graceful de tareas activas"""
        if not self.current_tasks:
            return
        
        self.logger.info(f"[SHUTDOWN] Gracefully stopping {len(self.current_tasks)} active tasks")
        
        # Dar tiempo a las tareas para completar
        try:
            await asyncio.wait_for(
                self._wait_for_tasks_completion(),
                timeout=self._shutdown_timeout
            )
        except asyncio.TimeoutError:
            self.logger.warning(f"[SHUTDOWN] Tasks did not complete in {self._shutdown_timeout}s, forcing stop")
        
        # Limpiar tareas restantes
        self.current_tasks.clear()
    
    async def _wait_for_tasks_completion(self):
        """Esperar a que las tareas activas se completen"""
        while self.current_tasks and not self._shutdown_event.is_set():
            await asyncio.sleep(0.5)
    
    async def _schedule_restart(self):
        """Programar restart del agente"""
        try:
            await asyncio.sleep(5)  # Esperar un poco antes de reiniciar
            await self.restart()
        except Exception as e:
            self.logger.error(f"[ERROR] Auto-restart failed: {e}")


# ============================================================================
# AGENTE DE EJEMPLO PARA TESTING Y DEMOSTRACIÓN
# ============================================================================

class ExampleGenesisAgent(GenesisAgent):
    """
    Agente de ejemplo - SOLO PARA TESTING Y DEMOSTRACIÓN
    
    Este agente demuestra cómo implementar un agente usando la clase base.
    NO ES PARA USO EN PRODUCCIÓN.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="example_agent",
            name="ExampleAgent",
            agent_type="example",
            capabilities=[AgentCapability.ARCHITECTURE_DESIGN],
            description="Example agent for testing and demonstration purposes",
            max_concurrent_tasks=2,
            default_timeout=120
        )
    
    async def _initialize_genesis_agent(self):
        """Inicialización del agente de ejemplo"""
        # Registrar handlers de tareas
        self.register_task_handler("test_task", self._handle_test_task)
        self.register_task_handler("echo_task", self._handle_echo_task)
        self.register_task_handler("slow_task", self._handle_slow_task)
        self.register_task_handler("error_task", self._handle_error_task)
        
        # Configuración de ejemplo
        self.set_config("example_setting", "example_value")
        self.set_config("max_items", 100)
        
        # Registrar middleware de ejemplo
        self.register_middleware(self._example_middleware)
        
        self.logger.info("[INIT] Example agent initialized with test handlers")
    
    async def _execute_task_implementation(self, task: AgentTask) -> TaskResult:
        """Implementación de ejemplo"""
        # Buscar handler para la tarea
        handler = self._task_handlers.get(task.name)
        if handler:
            return await handler(task)
        
        # Si no hay handler específico, retornar error
        return TaskResult(
            task_id=task.id,
            success=False,
            error=f"No handler registered for task: {task.name}",
            debug_info={"available_handlers": list(self._task_handlers.keys())}
        )
    
    async def _handle_test_task(self, task: AgentTask) -> TaskResult:
        """Handler de ejemplo para test_task"""
        # Simular trabajo
        await asyncio.sleep(0.1)
        
        message = task.params.get("message", "Hello from ExampleAgent!")
        
        return TaskResult(
            task_id=task.id,
            success=True,
            result={
                "message": message,
                "params": task.params,
                "agent_info": {
                    "name": self.name,
                    "type": self.agent_type,
                    "version": self.version
                }
            },
            metadata={"handler": "test_task", "example": True}
        )
    
    async def _handle_echo_task(self, task: AgentTask) -> TaskResult:
        """Handler que hace eco de los parámetros"""
        return TaskResult(
            task_id=task.id,
            success=True,
            result={"echo": task.params},
            metadata={"handler": "echo_task"}
        )
    
    async def _handle_slow_task(self, task: AgentTask) -> TaskResult:
        """Handler que simula una tarea lenta"""
        duration = task.params.get("duration", 2)
        await asyncio.sleep(duration)
        
        return TaskResult(
            task_id=task.id,
            success=True,
            result={"message": f"Slow task completed after {duration}s"},
            metadata={"handler": "slow_task", "duration": duration}
        )
    
    async def _handle_error_task(self, task: AgentTask) -> TaskResult:
        """Handler que simula errores para testing"""
        error_type = task.params.get("error_type", "generic")
        
        if error_type == "timeout":
            await asyncio.sleep(300)  # Provocar timeout
        elif error_type == "exception":
            raise Exception("Simulated exception for testing")
        elif error_type == "task_failure":
            return TaskResult(
                task_id=task.id,
                success=False,
                error="Simulated task failure"
            )
        
        return TaskResult(
            task_id=task.id,
            success=False,
            error=f"Unknown error type: {error_type}"
        )
    
    async def _example_middleware(self, task: AgentTask, phase: str, agent: 'GenesisAgent', result: TaskResult = None) -> Union[AgentTask, TaskResult]:
        """Middleware de ejemplo"""
        if phase == "pre":
            # Pre-processing: agregar timestamp a metadata
            task.metadata["middleware_start"] = datetime.utcnow().isoformat()
            self.logger.debug(f"[MIDDLEWARE] Pre-processing task {task.name}")
            return task
        elif phase == "post":
            # Post-processing: agregar duración a resultado
            if result:
                result.metadata["middleware_end"] = datetime.utcnow().isoformat()
                self.logger.debug(f"[MIDDLEWARE] Post-processing task {task.name}")
            return result
        
        return task if result is None else result