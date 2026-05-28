import asyncio
import logging
from typing import List, Dict

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from .config import TELEGRAM_BOT_TOKEN, MAX_CONTEXT_MESSAGES
from .ai_client import get_ai_response
from .knowledge_base import load_knowledge_base
from .prompts import SYSTEM_PROMPT
from .safety import (
    is_company_related, 
    get_safety_response,
    is_price_related,
    is_availability_related,
    is_vacancy_related,
    is_promotion_related
)
from .storage import ConversationStorage

# Настраиваем базовое логгирование (уровень INFO и выше будет выводиться в консоль)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализируем объекты бота и диспетчера из aiogram
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Создаём экземпляр нашего хранилища истории диалогов
# LIMIT_CONTEXT_MESSAGES берётся из конфига (по умолчанию 5)
storage = ConversationStorage(max_messages=MAX_CONTEXT_MESSAGES)

# Загружаем один раз базу знаний о компании при старте бота
KNOWLEDGE_BASE = load_knowledge_base()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    user_name = message.from_user.first_name or "Пользователь"
    welcome_text = (
        f"Здравствуйте, {user_name}! Я AI-ассистент компании «Центр Красок #1». "
        f"Могу рассказать о товарах, услугах, адресах, контактах, брендах, доставке и колеровке. "
        f"Просто напишите вопрос."
    )
    await message.answer(welcome_text)
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

@dp.message()
async def handle_message(message: Message):
    """Обработчик всех входящих текстовых сообщений."""
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    # Если сообщение пустое (или только пробелы) - просим пользователь написать что-то
    if not user_message:
        await message.answer("Пожалуйста, напишите ваш вопрос.")
        return
    
    # Показываем собеседнику, что бот "печатает" (улучшает UX)
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Сначала проверяем, относится ли вопрос вообще к нашей компании
        # Используем простую функцию из safety.py как первый фильтр
        if not is_company_related(user_message):
            # Если не related - даём стандартный безопасный ответ
            response = get_safety_response("general")
            await message.answer(response)
            
            # Всё равно сохраняем в историю диалога, чтобы сохранить контекст
            storage.add_message(user_id, "user", user_message)
            storage.add_message(user_id, "assistant", response)
            return
        
        # Проверяем специфичные типы вопросов, для которых есть заготовленные ответы
        # Это помогает избежать выдумывания AI и давать более точную информацию
        
        # Вопросы о ценах
        if is_price_related(user_message):
            response = get_safety_response("price")
            await message.answer(response)
            
            storage.add_message(user_id, "user", user_message)
            storage.add_message(user_id, "assistant", response)
            return
            
        # Вопросы о наличии товаров
        if is_availability_related(user_message):
            response = get_safety_response("availability")
            await message.answer(response)
            
            storage.add_message(user_id, "user", user_message)
            storage.add_message(user_id, "assistant", response)
            return
            
        # Вопросы о вакансиях
        if is_vacancy_related(user_message):
            response = get_safety_response("vacancy")
            await message.answer(response)
            
            storage.add_message(user_id, "user", user_message)
            storage.add_message(user_id, "assistant", response)
            return
            
        # Вопросы об акциях и скидках
        if is_promotion_related(user_message):
            response = get_safety_response("promotion")
            await message.answer(response)
            
            storage.add_message(user_id, "user", user_message)
            storage.add_message(user_id, "assistant", response)
            return
        
        # Если дошли до сюда - вопрос связан с компанией и не попал в специфичные категории
        # Получаем историю диалога для этого пользователя
        history = storage.get_history(user_id)
        
        # Запрашиваем ответ у AI, передавая ему сообщение пользователя, базу знаний и историю
        ai_response = get_ai_response(
            user_message=user_message,
            knowledge_base=KNOWLEDGE_BASE,
            conversation_history=history
        )
        
        # Отправляем полученный ответ пользователю
        await message.answer(ai_response)
        
        # Обновляем историю диалога: добавляем вопрос пользователя и ответ бота
        storage.add_message(user_id, "user", user_message)
        storage.add_message(user_id, "assistant", ai_response)
        
        # Логируем обработанное сообщение (обрезаем для краткости)
        logger.info(f"Обработано сообщение от пользователя {user_id}: {user_message[:50]}...")
        
    except Exception as e:
        # Ловим любые непредвиденные ошибки, чтобы бот не падал
        logger.error(f"Ошибка при обработке сообщения от пользователя {user_id}: {str(e)}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.")

# Экспортируем объекты, которые могут понадобиться в main.py (если решим разделить запуск)
__all__ = ["bot", "dp", "storage", "KNOWLEDGE_BASE"]