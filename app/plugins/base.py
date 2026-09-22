from abc import ABC, abstractmethod
from typing import Dict, Any, Callable

class BaseTaskPlugin(ABC):
    @abstractmethod
    def execute(self, task_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specific task logic and return output data."""
        pass

class TaskPluginRegistry:
    _registry: Dict[str, BaseTaskPlugin] = {}

    @classmethod
    def register(cls, task_type: str, plugin: BaseTaskPlugin):
        cls._registry[task_type] = plugin

    @classmethod
    def get(cls, task_type: str) -> BaseTaskPlugin:
        plugin = cls._registry.get(task_type)
        if not plugin:
            raise ValueError(f"No execution plugin registered for task type: '{task_type}'.")
        return plugin