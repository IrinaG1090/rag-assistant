# 📚 RAG Assistant — Документный ассистент на базе AI

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28-red)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📝 О проекте

**RAG Assistant** — это веб-приложение на базе Retrieval-Augmented Generation (RAG), которое позволяет задавать вопросы по вашим документам (PDF) и получать ответы с цитированием источников. Система использует векторную базу данных для поиска релевантных фрагментов и современные LLM для генерации ответов с учётом контекста.

### ✨ Возможности
- 📄 Загрузка PDF-документов и автоматическое создание векторной базы
- 🔍 Семантический поиск по содержимому документов
- 💬 Диалоговый режим с памятью (история сохраняется)
- 📊 Отображение источников ответов
- 🐳 Полная Docker-контейнеризация
- 🔐 Безопасное хранение токенов через `.env`

## 🛠️ Технологический стек

| Компонент | Технология |
|-----------|------------|
| **Язык** | Python 3.12 |
| **Веб-интерфейс** | Streamlit |
| **Векторная БД** | ChromaDB (с эмбеддингами all-MiniLM-L6-v2) |
| **LLM** | Hugging Face Inference API (meta-llama/Llama-3.2-3B-Instruct) |
| **Оркестрация** | LangChain 1.2 |
| **Контейнеризация** | Docker + Docker Compose |

## 📋 Предварительные требования

- Python 3.12+
- Docker и Docker Compose (опционально)
- Hugging Face API токен (получить на [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))

## 🚀 Быстрый старт

### Локальный запуск

1. **Клонировать репозиторий**
   ```bash
   git clone https://github.com/IrinaG1090/rag-assistant.git
   cd rag-assistant

2. **Создать виртуальное окружение и установить зависимости**
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   .\venv\Scripts\activate   # для Windows
   pip install -r requirements.txt 

3. **Настроить переменные окружения**
    cp .env.example .env
# Отредактируйте .env, добавьте свой HUGGINGFACEHUB_API_TOKEN

4. **Запустить приложение**
    streamlit run app/app.py

5. **Запуск через Docker**
    docker build -t rag-assistant .
    docker run -p 8501:8501 --env-file .env -v ./chroma_db:/app/chroma_db rag-assistant

6. **Или через Docker Compose:**
    docker-compose up

## Структура проекта
- `rag-assistant/`
  - `app/`
    - `app.py`
  - `notebooks/`
    - `01_index_document_v2.ipynb`
    - `03_conversational_rag.ipynb`
  - `chroma_db/`
  - `requirements.txt`
  - `requirements.in`
  - `Dockerfile`
  - `docker-compose.yml`
  - `.env.example`
  - `README.md`
  
## 🧪 Примеры запросов
После загрузки документа (например, научной статьи) можно задавать вопросы:

"Что такое in-context learning?"

"Кто основные авторы этого направления?"

"Какие методы сравниваются в статье?"

Система найдёт релевантные фрагменты и ответит на основе документа.

## 🗺️ Roadmap
Базовая RAG-система с локальной векторной БД

Поддержка диалоговой памяти

Веб-интерфейс на Streamlit

Docker-контейнеризация

Деплой в облако (AWS ECS/Fargate)

Поддержка нескольких форматов (DOCX, TXT)

Гибридный поиск (векторный + BM25)

## 🤝 Вклад в проект
Буду рада любым предложениям и улучшениям! Создавайте issue или отправляйте pull request.

## 📄 Лицензия
Проект распространяется под лицензией MIT. Подробнее в файле LICENSE.

## 🙏 Благодарности
Вдохновлено статьёй "A Survey on In-context Learning" Dong et al.

Hugging Face за отличные модели и API

LangChain за мощные инструменты для RAG

## Сделано с ❤️