import uuid
from dataclasses import dataclass
from typing import Optional, List
from dataclasses import field, asdict
from datetime import datetime

@dataclass
class TaskPostCall:
    title: str
    inputStr: str
    deadline: datetime
    requestId: Optional[str] = str(uuid.uuid4())

    def to_dict(self):
        """Converts the dataclass to a dictonary for easy serialization"""
        return asdict(self)
    
@dataclass
class TaskDetailQuery:
    id: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TaskUpdateCall:
    title: Optional[str] = None
    inputStr: Optional[str] = None
    deadline: Optional[datetime] = None
    
    def to_dict(self):
        return asdict(self)
    
@dataclass
class SubTaskPostCall:
    parent_task_id: str
    title: str
    deadline: datetime

    def to_dict(self):
        return asdict(self)

@dataclass
class SuccessResponse:
    successCode: int
    successResponse: str

    def to_dict(self):
        """Converts the dataclass to a dictonary for easy serialization"""
        return asdict(self)
    
@dataclass
class ErrorResponse:
    errorCode: int
    errorResponse: str
    errorResolution: Optional[str] = None

    def to_dict(self):
        """Converts the dataclass to a dictonary for easy serialization"""
        return asdict(self)

@dataclass
class TagSchema:
    _id: str
    name: str
    created_at: Optional[datetime] = datetime.now()

    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class TaskTagSchema:
    _id: str
    task_id: str
    tag_id: str
    created_at: Optional[datetime] = datetime.now()

    def to_dict(self):
        return {
            "_id": self._id,
            "task_id": self.task_id,
            "tag_id": self.tag_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class TaskSchema:
    _id: str
    title:  str
    description: str
    deadline: str
    priority: Optional[str] = 'Medium'
    completed: Optional[bool] = False
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    status: Optional[str] = 'Pending'
    tags: Optional[List[str]] = field(default_factory=list)
    parent_task_id: Optional[str] = None
    is_subtask: Optional[bool] = False

    def to_dict(self):
        return {
            "_id": self._id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status,
            "tags": self.tags,
            "parent_task_id": self.parent_task_id,
            "is_subtask": self.is_subtask
        }

@dataclass
class TaskListQuery:
    ordering: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    completed: Optional[bool] = None
    tag: Optional[str] = None

    def to_dict(self):
        return asdict(self)
    
    def has_any_filter(self) -> bool:
        """Check if at least one filter parameter is provided"""
        return any([
            self.ordering is not None,
            self.priority is not None,
            self.status is not None,
            self.completed is not None,
            self.tag is not None
        ])

@dataclass
class TaskListResponse:
    tasks: list
    total_count: int
    page: int = 1
    per_page: int = 10

    def to_dict(self):
        return {
            "tasks": self.tasks,
            "total_count": self.total_count,
            "page": self.page,
            "per_page": self.per_page
        }
    