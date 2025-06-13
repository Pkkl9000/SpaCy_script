# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY newapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY newapp/ .

# Загружаем английскую модель SpaCy
RUN python -m spacy download en_core_web_lg

# Открываем порт
EXPOSE 5000

# Запускаем приложение
CMD ["python", "app.py"]