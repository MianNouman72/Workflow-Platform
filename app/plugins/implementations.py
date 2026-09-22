import time
import requests
from typing import Dict, Any
from app.plugins.base import BaseTaskPlugin, TaskPluginRegistry

class HttpRequestPlugin(BaseTaskPlugin):
    def execute(self, task_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        url = task_config.get("url")
        method = task_config.get("method", "GET").upper()
        headers = task_config.get("headers", {})
        payload = task_config.get("payload", None)
        timeout = task_config.get("timeout", 30)

        if not url:
            raise ValueError("HTTP Request plugin requires a valid 'url' in configuration.")

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=payload,
            timeout=timeout
        )

        try:
            resp_data = response.json()
        except ValueError:
            resp_data = response.text

        return {
            "status_code": response.status_code,
            "response": resp_data,
            "headers": dict(response.headers)
        }

class DelayPlugin(BaseTaskPlugin):
    def execute(self, task_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        seconds = task_config.get("seconds", 0)
        if not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("Delay plugin requires a valid non-negative number of 'seconds'.")

        time.sleep(seconds)
        return {"delayed_seconds": seconds}

TaskPluginRegistry.register("HTTP_REQUEST", HttpRequestPlugin())
TaskPluginRegistry.register("DELAY", DelayPlugin())