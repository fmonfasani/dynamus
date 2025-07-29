class DynamusAgent:
    id: str
    actions: list[str]

    def execute(self, action: str, data: dict) -> dict:
        raise NotImplementedError
