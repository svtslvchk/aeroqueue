import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class TaskStatus(str, enum.Enum):
    """Статусы жизненного цикла задачи."""
    PENDING = "PENDING"          # Задача создана и ждет очереди
    PROCESSING = "PROCESSING"    # Воркер взял задачу в работу
    SUCCESS = "SUCCESS"          # Задача успешно выполнена
    FAILED = "FAILED"            # При выполнении задачи произошла ошибка


class Task(Base):
    """Модель для хранения метаданных и состояния задач."""
    __tablename__ = "tasks"

    # UUID как первичный ключ — стандарт для распределенных систем.
    # Это предотвращает перебор ID злоумышленниками (в отличие от обычного id: 1, 2, 3...)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Название выполняемой задачи (например: "tasks.send_email")
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Текущий статус задачи, ограниченный нашим Enum.
    # native_enum=False заставит SQLAlchemy хранить это как VARCHAR в БД, 
    # что упрощает будущие миграции, если мы захотим добавить новый статус.
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False),
        default=TaskStatus.PENDING,
        nullable=False,
    )

    # Параметры, с которыми была вызвана задача (аргументы функции).
    # Используем JSONB (двоичный JSON в PostgreSQL) — он работает быстрее и позволяет делать индексы.
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Результат работы задачи (то, что вернула функция). Nullable, пока задача не выполнена.
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Текст ошибки и traceback, если задача завершилась со статусом FAILED
    error_trace: Mapped[str | None] = mapped_column(String, nullable=True)

    # Временные метки (Timestamps) с временной зоной (timezone=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Время ставит сама БД в момент создания записи
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),        # БД будет автоматически обновлять это поле при любом UPDATE
        nullable=False,
    )