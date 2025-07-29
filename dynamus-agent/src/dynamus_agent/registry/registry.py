class AgentRegistry:
    _registry = {}

    @classmethod
    def register(cls, agent_cls):
        cls._registry[agent_cls.id] = agent_cls()

    @classmethod
    def get(cls, agent_id):
        return cls._registry.get(agent_id)

    @classmethod
    def all(cls):
        return cls._registry
