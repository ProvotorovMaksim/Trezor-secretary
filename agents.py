import os
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_gigachat.chat_models import GigaChat
from schemas import BotResponse, ClientProfile
from settings import settings
from sqlalchemy import select
from models import Client
from db_provider import async_session
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel("INFO")

# 2. Тулза (пока заглушка, позже заменим на asyncpg)
@tool
async def get_client_from_postgres(client_id: int) -> str:
    """Получает профиль клиента из реляционной БД (PostgreSQL) по ID."""
    try:
        async with async_session() as session:
            # session.get() — самый быстрый способ получить объект по первичному ключу
            try:
                client = await session.get(Client, client_id)
            except Exception as e: 
                logger.warning(f"Db_get clients exception: {e}")
                raise
            if client:
                # Формируем понятный текстовый контекст для GigaChat
                # Замените атрибуты (name, status, balance) на реальные поля вашей модели, если они называются иначе
                return (
                    f"Клиент найден. "
                    f"ID: {client.client_id}, "
                    f"Имя: {client.name}, "
                    f"Статус: {client.status}, "
                    f"Баланс: {client.balance}."
                    f"Изменён: {client.changed_at}"
                    f"Создан: {client.created_at}"
                )
            else:
                return f"Клиент с ID {client_id} не найден в базе данных."
                
    except Exception as e:
        return f"Ошибка при запросе к базе данных: {str(e)}"

from vector_db import vector_db

@tool
def search_similar_cases(query: str) -> str:
    """Ищет похожие кейсы и историю переписок в векторной БД по смыслу."""
    try:
        results = vector_db.search_similar(query, limit=3)
        
        if not results:
            return "Похожих кейсов не найдено."
        
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"{i}. {r['text']} (схожесть: {r['score']:.2f})")
        
        return "Найдены похожие кейсы:\n" + "\n".join(formatted)
        
    except Exception as e:
        return f"Ошибка поиска в векторной БД: {str(e)}"

# 3. Класс Оркестратора
class Orchestrator:
    def __init__(self):
        # Настройка LLM (замените на вашу, если не OpenAI)
        self.llm = GigaChat(
            credentials=settings.GIGACHAT_CREDENTIALS, # Ваши данные из кабинета разработчика Сбера
            model="GigaChat", # Или "GigaChat-Pro" в зависимости от доступа
            temperature=0.1,
            verify_ssl_certs=False # Часто требуется для корректной работы с серверами Сбера
        )


        # Агент
        self.analyst_agent = Agent(
            role="Аналитик данных CRM",
            goal="Найти информацию о клиенте в базе данных и сформулировать вежливый ответ",
            backstory="Ты эксперт по работе с реляционными базами данных. Ты всегда возвращаешь точные данные и формулируешь ответ кратко и по делу.",
            tools=[get_client_from_postgres, search_similar_cases],
            llm=self.llm,
            verbose=True # Показывает ход мыслей в консоли
        )

        # Задача с жесткой привязкой к Pydantic
        self.data_retrieval_task = Task(
            description="Найди профиль клиента с ID {client_id} в PostgreSQL. На основе полученных данных сформулируй ответ для клиента на его запрос: '{query}'.",
            expected_output="Структурированный ответ для отправки в Telegram и лог действия",
            agent=self.analyst_agent,
            output_pydantic=BotResponse # Результат будет строго этим объектом
        )

        # Crew (команда)
        self.crew = Crew(
            agents=[self.analyst_agent],
            tasks=[self.data_retrieval_task],
            process=Process.sequential,
            verbose=False
        )

    async def run(self, user_id: int, query: str) -> str:
        """Асинхронный запуск обработки сообщения."""
        try:
            # Асинхронный запуск, чтобы не блокировать бота
            result = await self.crew.kickoff_async(inputs={"client_id": user_id, "query": query})
            
            # Извлекаем наш строгий Pydantic-объект
            response_model: BotResponse = result.pydantic # type: ignore
            
            # Логирование действия (позже здесь будет запись в Redis/внутреннюю БД)
            print(f"[LOG CRM] User: {user_id} | Action: {response_model.action_log}")
            
            return response_model.message_to_client
            
        except Exception as e:
            print(f"Критическая ошибка в оркестраторе: {e}")
            return "Извините, произошла техническая ошибка. Я передал ваш запрос специалисту."
