class AgentRegistry:
    _registry = {}

    @classmethod
    def register(cls, agent_cls):
        """Register an agent class.

        The class must be instantiable without arguments and the resulting
        instance must expose an ``agent_id`` attribute. The instance is stored
        in the registry under this identifier.
        """

        agent = agent_cls()
        cls._registry[agent.agent_id] = agent

    @classmethod
    def get(cls, agent_id):
        """Retrieve a registered agent instance by its ``agent_id``."""

        return cls._registry.get(agent_id)

    @classmethod
    def all(cls):
        """Return the mapping of ``agent_id`` to agent instances."""

        return cls._registry
