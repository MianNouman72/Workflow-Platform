from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class WorkflowCreate(BaseModel):
    name: str

class WorkflowResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class WorkflowVersionCreate(BaseModel):
    workflow_id: int
    version: int
    definition: Dict[str, Any] = {}

class WorkflowVersionResponse(BaseModel):
    id: int
    workflow_id: int
    version: int
    definition: Dict[str, Any]

    class Config:
        from_attributes = True

class WorkflowTaskCreate(BaseModel):
    workflow_version_id: int
    task_key: str
    task_type: str
    config: Dict[str, Any] = {}
    dependency_ids: Optional[List[int]] = []  # Naya field DAG ke liye

class WorkflowTaskResponse(BaseModel):
    id: int
    workflow_version_id: int
    task_key: str
    task_type: str
    config: Dict[str, Any]
    dependency_ids: List[int] = []

    class Config:
        from_attributes = True

class WorkflowRunCreate(BaseModel):
    workflow_version_id: int

class WorkflowRunResponse(BaseModel):
    id: int
    workflow_version_id: int
    status: str

    class Config:
        from_attributes = True

class WorkflowRunUpdate(BaseModel):
    status: str