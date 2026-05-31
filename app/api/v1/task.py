from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

# Импортируем нашу зависимость БД. 
# (Если у тебя файл базы данных лежит в корне app, поправь путь на app.database)
from app.core.db import get_db_session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(tags=["Tasks"])


# Декоратор для POST-запроса. 
# response_model задает схему ответа, а status_code — правильный HTTP-статус при успехе
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Создание новой задачи в очереди.
    Принимает имя задачи и её полезную нагрузку (payload).
    Возвращает полную информацию о созданной задаче со статусом PENDING.
    """
    # 1. Переводим данные из Pydantic-схемы в SQLAlchemy-модель
    # task_in.model_dump() превращает входящий JSON в обычный python-словарь: {"name": "...", "payload": {...}}
    # Оператор ** распаковывает этот словарь в именованные аргументы для конструктора модели Task
    new_task = Task(**task_in.model_dump())

    # 2. Кладем объект в сессию (SQLAlchemy берет его "на карандаш", но в БД пока не отправляет)
    db.add(new_task)

    # 3. Фиксируем изменения (отправляем асинхронный SQL-запрос INSERT в PostgreSQL)
    await db.commit()

    # 4. "Освежаем" объект. База данных сгенерировала для нас UUID, статус PENDING и таймстампы.
    # Этот шаг заставляет SQLAlchemy перечитать эти автополя из БД обратно в Python-объект.
    await db.refresh(new_task)

    # Возвращаем объект модели. FastAPI посмотрит на response_model=TaskResponse,
    # увидит там `from_attributes=True` и сам соберет из этого объекта красивый JSON-ответ.
    return new_task


# GET-эндпоинт, который принимает в URL переменную task_id в формате UUID
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Получение информации о задаче по её уникальному UUID.
    Если задача не найдена в базе данных, возвращает ошибку 404 Not Found.
    """
    # 1. Формируем SQL-запрос: SELECT * FROM tasks WHERE tasks.id = :task_id
    query = select(Task).where(Task.id == task_id)

    # 2. Выполняем асинхронный запрос к PostgreSQL
    result = await db.execute(query)

    # 3. Извлекаем одну запись (или None, если ничего не нашлось)
    # scalar_one_or_none() идеально подходит для поиска по уникальному Primary Key
    task = result.scalar_one_or_none()

    # 4. Проверяем, нашлась ли задача. Если нет — бросаем 404 ошибку
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена в системе"
        )

    # 5. Если всё ок, возвращаем объект. FastAPI провалидирует его через TaskResponse
    return task
