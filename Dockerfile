# Берём базовый образ Python
FROM python:3.11-slim

# Создаём рабочую папку внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY app/requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем весь код
COPY app/ .

# Говорим какой порт использует приложение
EXPOSE 5000

# Команда запуска приложения
CMD ["python", "app.py"]