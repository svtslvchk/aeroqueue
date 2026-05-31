FROM python:3.12-slim

# Запрещаем Python писать файлы .pyc на диск и буферизировать логи
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Сначала копируем только зависимости (для кэширования слоев Docker)
COPY requirements.txt .

# Устанавливаем системные утилиты, если понадобятся, и зависимости Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем остальной код проекта
COPY . .

# Команда по умолчанию для запуска сервера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]