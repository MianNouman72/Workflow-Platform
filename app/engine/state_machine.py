from app.models import WorkflowStatus, TaskStatus

WORKFLOW_TRANSITIONS = {
    WorkflowStatus.CREATED: {WorkflowStatus.QUEUED, WorkflowStatus.CANCELLED},
    WorkflowStatus.QUEUED: {WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED, WorkflowStatus.PAUSED},
    WorkflowStatus.RUNNING: {WorkflowStatus.PAUSED, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED, WorkflowStatus.PARTIAL_FAILURE},
    WorkflowStatus.PAUSED: {WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.COMPLETED: set(),
    WorkflowStatus.FAILED: set(),
    WorkflowStatus.CANCELLED: set(),
    WorkflowStatus.PARTIAL_FAILURE: set()
}

TASK_TRANSITIONS = {
    TaskStatus.PENDING: {TaskStatus.QUEUED, TaskStatus.SKIPPED, TaskStatus.CANCELLED},
    TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.SKIPPED},
    TaskStatus.RUNNING: {TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.RETRYING, TaskStatus.TIMED_OUT, TaskStatus.CANCELLED},
    TaskStatus.RETRYING: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
    TaskStatus.SUCCESS: set(),
    TaskStatus.FAILED: {TaskStatus.QUEUED}, # For DLQ replay / manual retry
    TaskStatus.TIMED_OUT: {TaskStatus.QUEUED},
    TaskStatus.CANCELLED: set(),
    TaskStatus.SKIPPED: set()
}

def validate_workflow_transition(current_status: WorkflowStatus, target_status: WorkflowStatus) -> bool:
    if current_status == target_status:
        return True
    allowed = WORKFLOW_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise ValueError(f"Invalid workflow state transition from {current_status} to {target_status}.")
    return True

def validate_task_transition(current_status: TaskStatus, target_status: TaskStatus) -> bool:
    if current_status == target_status:
        return True
    allowed = TASK_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise ValueError(f"Invalid task state transition from {current_status} to {target_status}.")
    return True