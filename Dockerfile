# Используем официальный Python
FROM python:3.12-slim

# Рабочая директория
WORKDIR / app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY ..

# Указываем порт
ENV PORT 8080

# Запускаем FastAPI через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]