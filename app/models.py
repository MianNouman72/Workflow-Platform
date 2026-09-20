from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from .database import Base

# Task dependencies ke liye association table (DAG ke liye)
task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('parent_task_id', Integer, ForeignKey('workflow_tasks.id'), primary_key=True),
    Column('child_task_id', Integer, ForeignKey('workflow_tasks.id'), primary_key=True)
)

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    versions = relationship("WorkflowVersion", back_populates="workflow")

class WorkflowVersion(Base):
    __tablename__ = "workflow_versions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    version = Column(Integer)
    definition = Column(JSON, default={})

    workflow = relationship("Workflow", back_populates="versions")
    tasks = relationship("WorkflowTask", back_populates="version")

class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"

    id = Column(Integer, primary_key=True, index=True)
    workflow_version_id = Column(Integer, ForeignKey("workflow_versions.id"))
    task_key = Column(String, unique=True, index=True)
    task_type = Column(String)
    config = Column(JSON, default={})

    version = relationship("WorkflowVersion", back_populates="tasks")

    # Self-referential relationship for DAG dependencies
    dependencies = relationship(
        "WorkflowTask",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.child_task_id,
        secondaryjoin=id == task_dependencies.c.parent_task_id,
        backref="downstream_tasks"
    )

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_version_id = Column(Integer, ForeignKey("workflow_versions.id"))
    status = Column(String, default="PENDING")