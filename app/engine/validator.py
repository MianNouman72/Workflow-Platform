from typing import Dict, List, Any, Set

ALLOWED_TASK_TYPES = {
    "HTTP_REQUEST",
    "PYTHON_FUNCTION",
    "DELAY",
    "CONDITIONAL",
    "MAP",
    "REDUCE",
    "EMAIL_SIMULATOR",
    "DATABASE_QUERY"
}

def validate_workflow_definition(definition: Dict[str, Any]) -> None:
    if not isinstance(definition, dict) or "tasks" not in definition:
        raise ValueError("Malformed workflow definition: 'tasks' field is required.")

    tasks = definition["tasks"]
    if not isinstance(tasks, list) or len(tasks) == 0:
        raise ValueError("Workflow must contain at least one task.")

    task_ids: Set[str] = set()
    adj_list: Dict[str, List[str]] = {}
    in_degree: Dict[str, int] = {}

    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each task must be a dictionary.")
        
        task_id = task.get("id")
        if not task_id or not isinstance(task_id, str):
            raise ValueError("Each task must have a valid string 'id'.")

        if task_id in task_ids:
            raise ValueError(f"Duplicate task ID found: '{task_id}'.")
        task_ids.add(task_id)

        task_type = task.get("type")
        if task_type not in ALLOWED_TASK_TYPES:
            raise ValueError(f"Invalid task type '{task_type}' for task '{task_id}'.")

        dependencies = task.get("dependencies", [])
        if not isinstance(dependencies, list):
            raise ValueError(f"Dependencies for task '{task_id}' must be a list.")

        if task_id in dependencies:
            raise ValueError(f"Self-dependency detected in task '{task_id}'.")

        adj_list[task_id] = dependencies
        in_degree[task_id] = 0

    for task_id, dependencies in adj_list.items():
        for dep in dependencies:
            if dep not in task_ids:
                raise ValueError(f"Task '{task_id}' depends on non-existent task ID '{dep}'.")

    for task_id, dependencies in adj_list.items():
        for dep in dependencies:
            in_degree[task_id] += 1

    queue = [t_id for t_id, deg in in_degree.items() if deg == 0]
    visited_count = 0

    while queue:
        current = queue.pop(0)
        visited_count += 1

        for t_id, deps in adj_list.items():
            if current in deps:
                in_degree[t_id] -= 1
                if in_degree[t_id] == 0:
                    queue.append(t_id)

    if visited_count != len(tasks):
        raise ValueError("Cyclic dependency graph detected in workflow definition.")