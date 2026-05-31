from fastapi import FastAPI

from app.api.v1.task import router as tasks_router
from app.api.v1.auth import router as auth_router

# 1. Инициализируем экземпляр FastAPI
# Параметры внутри помогут Swagger-документации выглядеть красиво и профессионально
app = FastAPI(
    title="AeroQueue API",
    description="Backend для распределенной системы обработки задач (Очередь задач)",
    version="1.0.0",
)

# Подключаем роутер задач к приложению
# prefix="/api/v1/tasks" означает, что все эндпоинты из файла tasks.py 
# автоматически получат этот путь в начале URL
app.include_router(tasks_router, prefix="/api/v1/tasks")
# Подключаем роутер авторизации с префиксом /api/v1/auth
app.include_router(auth_router, prefix="/api/v1/auth")


# 2. Наш первый базовый эндпоинт (Healthcheck)
# Он нужен для того, чтобы другие сервисы (или Docker) могли проверить, жив ли наш сервер
@app.get("/", tags=["Healthcheck"])
async def health_check():
    """
    Эндпоинт для проверки работоспособности сервиса.
    Возвращает простой JSON со статусом 'working'.
    """
    return {
        "status": "working",
        "service": "aeroqueue-api",
    }