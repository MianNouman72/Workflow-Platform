from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.tasks import run_workflow_task

app = FastAPI(title="Distributed Workflow Orchestration Platform", version="1.0.0")

@app.get("/")
def health_check():
    return {"status": "healthy", "message": "Workflow Orchestration Platform is running."}

@app.post("/workflows/", status_code=status.HTTP_201_CREATED)
def create_workflow(payload: schemas.WorkflowCreate, db: Session = Depends(get_db)):
    from app.services.workflow_service import WorkflowService
    return WorkflowService.create_workflow(db=db, payload=payload)

@app.get("/workflows/", response_model=List[schemas.WorkflowResponse])
def list_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workflows = db.query(models.Workflow).offset(skip).limit(limit).all()
    return workflows

@app.post("/workflows/{workflow_id}/runs", status_code=status.HTTP_201_CREATED)
def trigger_workflow_run(workflow_id: int, db: Session = Depends(get_db)):
    try:
        workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Create a workflow run instance
        new_run = models.WorkflowRun(
            workflow_id=workflow_id,
            status="QUEUED"
        )
        db.add(new_run)
        db.commit()
        db.refresh(new_run)
        
        # Trigger the Celery background task
        run_workflow_task.delay(new_run.id)
        
        return {
            "run_id": new_run.id,
            "workflow_id": workflow_id,
            "status": new_run.status,
            "message": "Workflow run triggered and queued successfully."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/runs/{run_id}")
def get_workflow_run_status(run_id: int, db: Session = Depends(get_db)):
    run = db.query(models.WorkflowRun).filter(models.WorkflowRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    
    return {
        "run_id": run.id,
        "workflow_id": run.workflow_id,
        "status": run.status,
        "created_at": getattr(run, "created_at", None),
        "updated_at": getattr(run, "updated_at", None)
    }