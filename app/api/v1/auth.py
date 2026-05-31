from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter(tags=["Authentication"])


# Инициализируем схему HTTPBearer. 
# auto_error=True означает, что если токена вообще нет в заголовках, 
# FastAPI сам сразу вернет клиенту ошибку 403 Forbidden.
security_scheme = HTTPBearer(auto_error=True)


# Схема для валидации входящего запроса на вход
class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(credentials: LoginRequest):
    """
    Эндпоинт для входа в систему (Аутентификация).
    Для теста используй: admin / secret
    В ответ возвращается фиксированный Bearer-токен.
    """
    # Хардкодим проверку для нашей заглушки
    if credentials.username == "admin" and credentials.password == "secret":
        return {
            "access_token": "fake-super-secure-jwt-token-for-aeroqueue",
            "token_type": "bearer"
        }

    # Если логин/пароль не подошли — возвращаем стандартный HTTP 401 Unauthorized
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверное имя пользователя или пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    Зависимость для защиты эндпоинтов.
    Извлекает Bearer-токен из заголовка Authorization и сверяет его с нашей заглушкой.
    """
    # credentials.credentials содержит чистую строку токена (без слова 'Bearer')
    token = credentials.credentials
    
    # Сверяем токен с нашей фейк-строкой из эндпоинта login
    if token != "fake-super-secure-jwt-token-for-aeroqueue":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Возвращаем условного пользователя (в будущем тут будет объект юзера из базы данных)
    return {"username": "admin", "role": "superuser"}