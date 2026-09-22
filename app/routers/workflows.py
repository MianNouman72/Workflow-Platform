from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
import traceback

from app.database import get_db
from app.models import Workflow, WorkflowVersion, User
from app.engine.validator import validate_workflow_definition

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_workflow(payload: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        base_name = payload.get("name")
        description = payload.get("description", "")
        definition = payload.get("definition")

        if not base_name or not definition:
            raise HTTPException(status_code=400, detail="Workflow name and definition are required.")

        validate_workflow_definition(definition)

        # Loop to ensure absolute uniqueness against database constraints
        name = base_name
        while db.query(Workflow).filter(Workflow.name == name).first():
            name = f"{base_name}_{uuid.uuid4().hex[:6]}"

        default_user = db.query(User).first()
        if not default_user:
            default_user = User(
                username="admin", 
                email="admin@platform.com", 
                hashed_password="dummy_hashed_password", 
                role="ADMIN"
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)

        workflow = Workflow(name=name, description=description, created_by_id=default_user.id)
        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        version = WorkflowVersion(
            workflow_id=workflow.id,
            version_number=1,
            definition=definition,
            created_by_id=default_user.id
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        return {
            "workflow_id": workflow.id,
            "version_id": version.id,
            "name": workflow.name,
            "version": version.version_number,
            "message": "Workflow created and validated successfully."
        }
    except Exception as e:
        db.rollback()
        error_detail = traceback.format_exc()
        print(error_detail)
        raise HTTPException(status_code=500, detail=str(e))