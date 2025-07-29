# src/genesis_agents/base/capabilities.py
"""
Definición de capacidades de agentes Genesis - Hub Independiente

Estas capacidades son el "contrato" entre el hub y los agentes específicos.
Cada agente en el ecosistema debe declarar qué capacidades tiene.
"""

from enum import Enum
from typing import Dict, List, Set


class AgentCapability(str, Enum):
    """
    Capacidades que pueden tener los agentes Genesis
    
    Organizadas por dominios funcionales
    """
    
    # ===== ARQUITECTURA Y DISEÑO =====
    ARCHITECTURE_DESIGN = "architecture_design"
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    SCHEMA_GENERATION = "schema_generation"
    TECHNOLOGY_SELECTION = "technology_selection"
    PATTERN_RECOMMENDATION = "pattern_recommendation"
    
    # ===== BACKEND DEVELOPMENT =====
    API_GENERATION = "api_generation"
    DATABASE_MODELING = "database_modeling"
    AUTH_IMPLEMENTATION = "auth_implementation"
    BUSINESS_LOGIC = "business_logic"
    DATA_VALIDATION = "data_validation"
    MIDDLEWARE_SETUP = "middleware_setup"
    
    # ===== FRONTEND DEVELOPMENT =====
    UI_GENERATION = "ui_generation"
    COMPONENT_CREATION = "component_creation"
    STATE_MANAGEMENT = "state_management"
    ROUTING_SETUP = "routing_setup"
    STYLING = "styling"
    RESPONSIVE_DESIGN = "responsive_design"
    
    # ===== DEVOPS Y INFRAESTRUCTURA =====
    CONTAINERIZATION = "containerization"
    CI_CD_SETUP = "ci_cd_setup"
    DEPLOYMENT_CONFIG = "deployment_config"
    MONITORING_SETUP = "monitoring_setup"
    INFRASTRUCTURE_CODE = "infrastructure_code"
    SCALING_CONFIG = "scaling_config"
    
    # ===== INTELIGENCIA ARTIFICIAL =====
    LLM_INTEGRATION = "llm_integration"
    VECTOR_DB_SETUP = "vector_db_setup"
    AI_WORKFLOW = "ai_workflow"
    EMBEDDING_GENERATION = "embedding_generation"
    PROMPT_ENGINEERING = "prompt_engineering"
    ML_PIPELINE = "ml_pipeline"
    
    # ===== PERFORMANCE Y OPTIMIZACIÓN =====
    CODE_OPTIMIZATION = "code_optimization"
    SECURITY_HARDENING = "security_hardening"
    PERFORMANCE_TUNING = "performance_tuning"
    LOAD_TESTING = "load_testing"
    CACHING_SETUP = "caching_setup"
    
    # ===== TESTING Y CALIDAD =====
    UNIT_TESTING = "unit_testing"
    INTEGRATION_TESTING = "integration_testing"
    E2E_TESTING = "e2e_testing"
    CODE_REVIEW = "code_review"
    QUALITY_ASSURANCE = "quality_assurance"
    
    # ===== DOCUMENTACIÓN =====
    API_DOCUMENTATION = "api_documentation"
    USER_DOCUMENTATION = "user_documentation"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    
    # ===== DEPLOYMENT ESPECIALIZADO =====
    CLOUD_DEPLOYMENT = "cloud_deployment"
    KUBERNETES_DEPLOYMENT = "kubernetes_deployment"
    SERVERLESS_DEPLOYMENT = "serverless_deployment"
    DATABASE_DEPLOYMENT = "database_deployment"


class CapabilityCategory(str, Enum):
    """Categorías de capacidades para organización"""
    ARCHITECTURE = "architecture"
    BACKEND = "backend"
    FRONTEND = "frontend"
    DEVOPS = "devops"
    AI = "ai"
    PERFORMANCE = "performance"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"


# Mapeo de capacidades a categorías
CAPABILITY_CATEGORIES: Dict[AgentCapability, CapabilityCategory] = {
    # Arquitectura
    AgentCapability.ARCHITECTURE_DESIGN: CapabilityCategory.ARCHITECTURE,
    AgentCapability.REQUIREMENT_ANALYSIS: CapabilityCategory.ARCHITECTURE,
    AgentCapability.SCHEMA_GENERATION: CapabilityCategory.ARCHITECTURE,
    AgentCapability.TECHNOLOGY_SELECTION: CapabilityCategory.ARCHITECTURE,
    AgentCapability.PATTERN_RECOMMENDATION: CapabilityCategory.ARCHITECTURE,
    
    # Backend
    AgentCapability.API_GENERATION: CapabilityCategory.BACKEND,
    AgentCapability.DATABASE_MODELING: CapabilityCategory.BACKEND,
    AgentCapability.AUTH_IMPLEMENTATION: CapabilityCategory.BACKEND,
    AgentCapability.BUSINESS_LOGIC: CapabilityCategory.BACKEND,
    AgentCapability.DATA_VALIDATION: CapabilityCategory.BACKEND,
    AgentCapability.MIDDLEWARE_SETUP: CapabilityCategory.BACKEND,
    
    # Frontend
    AgentCapability.UI_GENERATION: CapabilityCategory.FRONTEND,
    AgentCapability.COMPONENT_CREATION: CapabilityCategory.FRONTEND,
    AgentCapability.STATE_MANAGEMENT: CapabilityCategory.FRONTEND,
    AgentCapability.ROUTING_SETUP: CapabilityCategory.FRONTEND,
    AgentCapability.STYLING: CapabilityCategory.FRONTEND,
    AgentCapability.RESPONSIVE_DESIGN: CapabilityCategory.FRONTEND,
    
    # DevOps
    AgentCapability.CONTAINERIZATION: CapabilityCategory.DEVOPS,
    AgentCapability.CI_CD_SETUP: CapabilityCategory.DEVOPS,
    AgentCapability.DEPLOYMENT_CONFIG: CapabilityCategory.DEVOPS,
    AgentCapability.MONITORING_SETUP: CapabilityCategory.DEVOPS,
    AgentCapability.INFRASTRUCTURE_CODE: CapabilityCategory.DEVOPS,
    AgentCapability.SCALING_CONFIG: CapabilityCategory.DEVOPS,
    
    # AI
    AgentCapability.LLM_INTEGRATION: CapabilityCategory.AI,
    AgentCapability.VECTOR_DB_SETUP: CapabilityCategory.AI,
    AgentCapability.AI_WORKFLOW: CapabilityCategory.AI,
    AgentCapability.EMBEDDING_GENERATION: CapabilityCategory.AI,
    AgentCapability.PROMPT_ENGINEERING: CapabilityCategory.AI,
    AgentCapability.ML_PIPELINE: CapabilityCategory.AI,
    
    # Performance
    AgentCapability.CODE_OPTIMIZATION: CapabilityCategory.PERFORMANCE,
    AgentCapability.SECURITY_HARDENING: CapabilityCategory.PERFORMANCE,
    AgentCapability.PERFORMANCE_TUNING: CapabilityCategory.PERFORMANCE,
    AgentCapability.LOAD_TESTING: CapabilityCategory.PERFORMANCE,
    AgentCapability.CACHING_SETUP: CapabilityCategory.PERFORMANCE,
    
    # Testing
    AgentCapability.UNIT_TESTING: CapabilityCategory.TESTING,
    AgentCapability.INTEGRATION_TESTING: CapabilityCategory.TESTING,
    AgentCapability.E2E_TESTING: CapabilityCategory.TESTING,
    AgentCapability.CODE_REVIEW: CapabilityCategory.TESTING,
    AgentCapability.QUALITY_ASSURANCE: CapabilityCategory.TESTING,
    
    # Documentation
    AgentCapability.API_DOCUMENTATION: CapabilityCategory.DOCUMENTATION,
    AgentCapability.USER_DOCUMENTATION: CapabilityCategory.DOCUMENTATION,
    AgentCapability.TECHNICAL_DOCUMENTATION: CapabilityCategory.DOCUMENTATION,
    
    # Deployment
    AgentCapability.CLOUD_DEPLOYMENT: CapabilityCategory.DEPLOYMENT,
    AgentCapability.KUBERNETES_DEPLOYMENT: CapabilityCategory.DEPLOYMENT,
    AgentCapability.SERVERLESS_DEPLOYMENT: CapabilityCategory.DEPLOYMENT,
    AgentCapability.DATABASE_DEPLOYMENT: CapabilityCategory.DEPLOYMENT,
}


def get_capabilities_by_category(category: CapabilityCategory) -> List[AgentCapability]:
    """Obtener capacidades por categoría"""
    return [
        capability for capability, cat in CAPABILITY_CATEGORIES.items()
        if cat == category
    ]


def get_capability_category(capability: AgentCapability) -> CapabilityCategory:
    """Obtener categoría de una capacidad"""
    return CAPABILITY_CATEGORIES.get(capability, CapabilityCategory.ARCHITECTURE)


def validate_capability_combination(capabilities: List[AgentCapability]) -> bool:
    """
    Validar que una combinación de capacidades sea coherente
    
    Algunas combinaciones pueden no tener sentido (ej: solo documentation + deployment)
    """
    if not capabilities:
        return False
    
    categories = set(get_capability_category(cap) for cap in capabilities)
    
    # Un agente debe tener al menos una capacidad "productiva"
    productive_categories = {
        CapabilityCategory.ARCHITECTURE,
        CapabilityCategory.BACKEND,
        CapabilityCategory.FRONTEND,
        CapabilityCategory.DEVOPS,
        CapabilityCategory.AI
    }
    
    return bool(categories.intersection(productive_categories))


# Capacidades comunes por tipo de agente (para referencia)
COMMON_AGENT_CAPABILITIES = {
    "architect": [
        AgentCapability.ARCHITECTURE_DESIGN,
        AgentCapability.REQUIREMENT_ANALYSIS,
        AgentCapability.SCHEMA_GENERATION,
        AgentCapability.TECHNOLOGY_SELECTION,
        AgentCapability.PATTERN_RECOMMENDATION
    ],
    "backend": [
        AgentCapability.API_GENERATION,
        AgentCapability.DATABASE_MODELING,
        AgentCapability.AUTH_IMPLEMENTATION,
        AgentCapability.BUSINESS_LOGIC,
        AgentCapability.DATA_VALIDATION
    ],
    "frontend": [
        AgentCapability.UI_GENERATION,
        AgentCapability.COMPONENT_CREATION,
        AgentCapability.STATE_MANAGEMENT,
        AgentCapability.ROUTING_SETUP,
        AgentCapability.STYLING
    ],
    "devops": [
        AgentCapability.CONTAINERIZATION,
        AgentCapability.CI_CD_SETUP,
        AgentCapability.DEPLOYMENT_CONFIG,
        AgentCapability.MONITORING_SETUP,
        AgentCapability.INFRASTRUCTURE_CODE
    ],
    "ai": [
        AgentCapability.LLM_INTEGRATION,
        AgentCapability.VECTOR_DB_SETUP,
        AgentCapability.AI_WORKFLOW,
        AgentCapability.EMBEDDING_GENERATION,
        AgentCapability.PROMPT_ENGINEERING
    ]
}