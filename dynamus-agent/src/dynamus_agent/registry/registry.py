class AgentRegistry:
    _registry = {}

    @classmethod
    def register(cls, agent_cls):
        """Register an agent class.

        ``agent_cls`` must be instantiable without arguments. During
        registration, the class is instantiated and the resulting object is
        expected to expose an ``agent_id`` attribute used as the registry key.

        Raises:
            ValueError: If instantiation fails or the instance lacks an
                ``agent_id`` attribute.
        """

        try:
            agent = agent_cls()
        except Exception as exc:  # noqa: BLE001 - propagate as ValueError
            raise ValueError(
                f"Failed to instantiate agent class {agent_cls!r}"
            ) from exc

        if not hasattr(agent, "agent_id"):
            raise ValueError(
                f"Agent instance of {agent_cls.__name__} must define 'agent_id'"
            )

        cls._registry[agent.agent_id] = agent

    @classmethod
    def get(cls, agent_id):
        """Retrieve a registered agent instance by its ``agent_id``."""

        return cls._registry.get(agent_id)

    @classmethod
    def all(cls):
        """Return the mapping of ``agent_id`` to agent instances."""

        return cls._registry
