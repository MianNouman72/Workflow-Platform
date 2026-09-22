from app.celery_app import celery_app
from app.database import SessionLocal
from app import models

@celery_app.task(bind=True)
def run_workflow_task(self, run_id: int):
    db = SessionLocal()
    try:
        # Fetch the workflow run from database
        run = db.query(models.WorkflowRun).filter(models.WorkflowRun.id == run_id).first()
        if not run:
            print(f"--> Error: Run ID {run_id} not found in database!")
            return {"error": "Run not found"}
            
        # Fetch tasks associated with the workflow version using version_id safely
        tasks = []
        if hasattr(models.WorkflowTask, "workflow_version_id") and getattr(run, "version_id", None):
            tasks = db.query(models.WorkflowTask).filter(models.WorkflowTask.workflow_version_id == run.version_id).all()
        
        # DAG Execution logic simulation
        for task in tasks:
            parent_keys = [p.task_key for p in task.dependencies] if hasattr(task, "dependencies") else []
            print(f"Background Executing Task: {getattr(task, 'task_key', 'unknown')} (Depends on: {parent_keys})")
            
        # Update status to SUCCESS and commit
        run.status = "SUCCESS"
        db.commit()
        db.refresh(run)
        
        print(f"--> SUCCESS: Workflow run {run_id} successfully updated in database to SUCCESS!")
        return {"run_id": run_id, "status": "SUCCESS"}
        
    except Exception as e:
        db.rollback()
        print(f"--> EXCEPTION in task for run {run_id}: {str(e)}")
        try:
            if 'run' in locals() and run:
                run.status = "FAILED"
                db.commit()
        except Exception as commit_err:
            print(f"--> Failed to update status to FAILED: {str(commit_err)}")
        raise e
        
    finally:
        db.close()