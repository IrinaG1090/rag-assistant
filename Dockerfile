FROM python:3.12.7-slim

WORKDIR /app

# 1. Копируем ТОЛЬКО файл с зависимостями (меняется редко)
COPY requirements.txt ./

# 2. Устанавливаем зависимости (выполнится 1 раз и закэшируется)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Копируем всё остальное (меняется часто, кэш не сбросит предыдущий слой)
COPY . .

# Указываем порт для Streamlit
EXPOSE 8501

CMD ["streamlit", "run", "app/app.py", "--server.port=7860", "--server.address=0.0.0.0"]