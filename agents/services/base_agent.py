from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, model_name="llama3.2", secondary_model_name="None"):
        self.model_name = model_name
        secondary_model_name = secondary_model_name

    @abstractmethod
    async def process(self, *args, **kwargs):
        pass

    @abstractmethod
    async def generate_response(self, *args, **kwargs):
        pass
