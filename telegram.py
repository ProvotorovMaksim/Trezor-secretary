import asyncio
from aiogram import Bot, Dispatcher, types, F
from agents import Orchestrator # Ваш класс оркестратора агентов
from settings import settings

bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализация ваших баз данных и агентов
# db_relational = RelationalDB()
# db_internal = InternalDB()
orchestrator = Orchestrator() 

@dp.message(F.business_connection_id)
async def handle_business_message(message: types.Message):
    if not message.text:
        return

    client_id = message.from_user.id # type: ignore
    client_text = message.text 
    
    # 1. Агенты обрабатывают запрос (асинхронно, чтобы не блокировать бота)
    # Внутри orchestrator.run() происходит выбор агента, запросы к БД и генерация
    agent_response = await orchestrator.run(
        user_id=client_id, 
        query=client_text
    )
    
    # 2. Отправляем ответ от вашего имени
    await message.answer(agent_response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
