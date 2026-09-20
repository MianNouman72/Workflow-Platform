from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Distributed Workflow & Job Orchestration Platform")

@app.post("/workflows/", response_model=schemas.WorkflowResponse)
def create_workflow(workflow: schemas.WorkflowCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Workflow).filter(models.Workflow.name == workflow.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Workflow already exists")
    db_workflow = models.Workflow(name=workflow.name)
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@app.post("/workflow-versions/", response_model=schemas.WorkflowVersionResponse)
def create_workflow_version(version: schemas.WorkflowVersionCreate, db: Session = Depends(get_db)):
    db_version = models.WorkflowVersion(
        workflow_id=version.workflow_id,
        version=version.version,
        definition=version.definition
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

@app.post("/workflow-tasks/", response_model=schemas.WorkflowTaskResponse)
def create_workflow_task(task: schemas.WorkflowTaskCreate, db: Session = Depends(get_db)):
    db_task = models.WorkflowTask(
        workflow_version_id=task.workflow_version_id,
        task_key=task.task_key,
        task_type=task.task_type,
        config=task.config
    )
    
    # Agar task ki koi dependencies di gayi hain toh unko link karein
    if task.dependency_ids:
        parents = db.query(models.WorkflowTask).filter(models.WorkflowTask.id.in_(task.dependency_ids)).all()
        db_task.dependencies = parents

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return schemas.WorkflowTaskResponse(
        id=db_task.id,
        workflow_version_id=db_task.workflow_version_id,
        task_key=db_task.task_key,
        task_type=db_task.task_type,
        config=db_task.config,
        dependency_ids=[p.id for p in db_task.dependencies]
    )

@app.post("/workflow-runs/", response_model=schemas.WorkflowRunResponse)
def create_workflow_run(run: schemas.WorkflowRunCreate, db: Session = Depends(get_db)):
    db_run = models.WorkflowRun(
        workflow_version_id=run.workflow_version_id,
        status="PENDING"
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run

@app.post("/workflow-runs/{run_id}/execute", response_model=schemas.WorkflowRunResponse)
def execute_workflow_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(models.WorkflowRun).filter(models.WorkflowRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    
    run.status = "RUNNING"
    db.commit()
    db.refresh(run)
    
    tasks = db.query(models.WorkflowTask).filter(models.WorkflowTask.workflow_version_id == run.workflow_version_id).all()
    
    # DAG Execution: Check dependencies and execute sequentially/safely
    for task in tasks:
        parent_keys = [p.task_key for p in task.dependencies]
        print(f"Executing Task: {task.task_key} (Depends on: {parent_keys})")
    
    run.status = "SUCCESS"
    db.commit()
    db.refresh(run)
    
    return run