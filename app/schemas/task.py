from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import TaskStatus


# 1. Схема для ВХОДЯЩИХ данных (создание задачи)
class TaskCreate(BaseModel):
    name: str = Field(
        ...,
        description="Название задачи/воркера, например 'tasks.send_email'",
        min_length=3,
        max_length=255
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON-объект с произвольными параметрами для выполнения задачи"
    )


# 2. Схема для ИСХОДЯЩИХ данных (ответ клиенту)
class TaskResponse(BaseModel):
    id: UUID
    name: str
    status: TaskStatus
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_trace: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Включаем интеграцию с ОРМ (SQLAlchemy)
    # В Pydantic v2 это делается через ConfigDict
    model_config = ConfigDict(from_attributes=True)