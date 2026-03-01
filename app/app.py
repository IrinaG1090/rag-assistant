import streamlit as st
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import time

# Загружаем переменные окружения
load_dotenv()

# Настройка страницы
st.set_page_config(
    page_title="RAG Ассистент по документам",
    page_icon="📚",
    layout="wide"
)

# Заголовок
st.title("📚 RAG Ассистент по документам")
st.markdown("Загрузи PDF и задавай вопросы по его содержанию")

# --- Инициализация клиента HuggingFace ---
@st.cache_resource
def get_hf_client():
    """Инициализирует клиент HuggingFace (кэшируется)"""
    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not hf_token:
        hf_token = st.text_input("Введите ваш HuggingFace токен:", type="password")
        if not hf_token:
            st.warning("Пожалуйста, введите токен для продолжения")
            st.stop()
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token
    
    # Используем ту же модель, что работала в ноутбуке
    client = InferenceClient(
        model="meta-llama/Llama-3.2-3B-Instruct",
        token=hf_token,
        provider="together"  # Явно указываем провайдера
    )
    return client

# --- Инициализация эмбеддингов ---
@st.cache_resource
def get_embeddings():
    """Инициализирует модель эмбеддингов (кэшируется)"""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

# --- Загрузка векторной базы ---
@st.cache_resource
def load_vector_db(db_path):
    """Загружает векторную базу из указанной папки"""
    embeddings = get_embeddings()
    if os.path.exists(db_path):
        vectordb = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings
        )
        return vectordb
    return None

# --- Функция для вызова модели ---
def call_llm(messages, client):
    """Отправляет сообщения в модель и получает ответ"""
    try:
        response = client.chat.completions.create(
            messages=messages,
            max_tokens=512,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {str(e)}"

# --- Функция для создания RAG-ответа ---
def get_rag_response(question, vectordb, client, chat_history):
    """Формирует ответ с учётом контекста из базы и истории"""
    
    # 1. Ищем релевантные чанки
    docs = vectordb.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # 2. Формируем сообщения с историей и контекстом
    messages = []
    
    # Добавляем системный промпт с контекстом
    messages.append({
        "role": "system", 
        "content": f"Ты ассистент, отвечающий на вопросы по документам. Используй следующий контекст для ответа. Если ответа нет в контексте, скажи, что не знаешь.\n\nКонтекст:\n{context}"
    })
    
    # Добавляем историю диалога (последние 4 сообщения)
    for msg in chat_history[-4:]:
        messages.append(msg)
    
    # Добавляем текущий вопрос
    messages.append({"role": "user", "content": question})
    
    # 3. Получаем ответ
    response = call_llm(messages, client)
    
    return response, docs

# --- Функция для обработки нового PDF ---
def process_pdf(uploaded_file, embeddings):
    """Загружает PDF, создаёт чанки и векторную базу"""
    
    # Сохраняем загруженный файл временно
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Загружаем PDF
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        
        # Разбиваем на чанки
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)
        
        # Создаём векторную базу
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./chroma_db_custom"
        )
        
        return vectordb, f"✅ Обработано {len(documents)} страниц, создано {len(chunks)} чанков"
    
    finally:
        # Удаляем временный файл
        os.unlink(tmp_path)

# --- Инициализация хранилища сессий ---
if "store" not in st.session_state:
    st.session_state.store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Возвращает историю для session_id"""
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = []
    return st.session_state.store[session_id]

# --- Боковая панель ---
with st.sidebar:
    st.header("⚙️ Настройки")
    
    # Инициализация клиента
    client = get_hf_client()
    
    st.divider()
    
    # Выбор источника базы данных
    st.subheader("📁 Источник данных")
    
    db_option = st.radio(
        "Выберите источник:",
        ["Использовать готовую базу (chroma_db)", "Загрузить новый PDF"]
    )
    
    vectordb = None
    db_status = ""
    
    if db_option == "Использовать готовую базу (chroma_db)":
        vectordb = load_vector_db("./chroma_db")
        if vectordb:
            db_status = f"✅ База загружена, векторов: {vectordb._collection.count()}"
        else:
            db_status = "❌ База не найдена. Сначала создайте её через ноутбук или загрузите PDF"
    
    else:  # Загрузить новый PDF
        uploaded_file = st.file_uploader("Выберите PDF файл", type="pdf")
        if uploaded_file is not None:
            with st.spinner("Обрабатываю PDF..."):
                embeddings = get_embeddings()
                vectordb, status_msg = process_pdf(uploaded_file, embeddings)
                db_status = status_msg
                if vectordb:
                    st.success("✅ База создана!")
    
    if db_status:
        st.info(db_status)
    
    st.divider()
    
    # Кнопка очистки истории
    if st.button("🗑️ Очистить историю"):
        if "session_id" in st.session_state:
            st.session_state.store[st.session_state.session_id] = []
        st.rerun()

# --- Основная область (чат) ---
if vectordb is None:
    st.warning("👈 Пожалуйста, выберите источник данных в боковой панели")
    st.stop()

# Уникальный ID сессии (можно использовать IP или просто фиксированный)
if "session_id" not in st.session_state:
    st.session_state.session_id = "web_user_1"

# Получаем историю для текущей сессии
chat_history = get_session_history(st.session_state.session_id)

# Отображаем историю чата
for message in chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода вопроса
if prompt := st.chat_input("Задайте вопрос по документу"):
    
    # Добавляем вопрос пользователя в историю и отображаем
    chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Получаем ответ
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            response, docs = get_rag_response(prompt, vectordb, client, chat_history)
            st.markdown(response)
            
            # Показываем источники в экспандере
            with st.expander("📚 Источники"):
                for i, doc in enumerate(docs):
                    st.markdown(f"**Фрагмент {i+1}:**")
                    st.markdown(doc.page_content[:300] + "...")
    
    # Добавляем ответ в историю
    chat_history.append({"role": "assistant", "content": response})