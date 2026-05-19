FROM python:3.11-slim

WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Открываем порт
EXPOSE 8005

# Команда для запуска
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8005"]