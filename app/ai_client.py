import logging
import requests
import json
from typing import List, Dict, Optional
from .config import GROK_API_KEY, GROK_MODEL
from .prompts import SYSTEM_PROMPT

# Настраиваем логгирование, чтобы видеть, что происходит в боте (полезно для отладки)
logger = logging.getLogger(__name__)

def get_ai_response(
    user_message: str,
    knowledge_base: str,
    conversation_history: List[Dict[str, str]] = None,
    max_tokens: int = 500,
    temperature: float = 0.2
) -> str:
    """
    Получает ответ от Grok API (xAI) на основе сообщения пользователя, базы знаний и истории диалога.
    
    Args:
        user_message (str): Вопрос/сообщение пользователя
        knowledge_base (str): Содержимое базы знаний о компании
        conversation_history (List[Dict]): История диалога (список словарей с ролью и текстом)
        max_tokens (int): Максимальное количество токенов в ответе
        temperature (float): Температура семплинга (от 0.0 до 1.0, меньше - более предсказуемо)
        
    Returns:
        str: Ответ, сгенерированный AI
    """
    try:
        # Формируем сообщения для отправки в Grok API
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        
        # Добавляем базу знаний как отдельное системное сообщение
        messages.append({
            "role": "system", 
            "content": f"База знаний о компании:\n\n{knowledge_base}"
        })
        
        # Если есть история диалога, добавляем её
        if conversation_history:
            for msg in conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": user_message})
        
        # Grok API endpoint (xAI)
        api_url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GROK_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        # Выполняем запрос
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Grok API error: {response.status_code} - {response.text}")
            return "Произошла ошибка при обращении к AI API. Пожалуйста, попробуйте позже."
        
        # Парсим ответ
        result = response.json()
        # Извлекаем текст ответа
        if "choices" in result and len(result["choices"]) > 0:
            ai_response = result["choices"][0].get("message", {}).get("content", "").strip()
        else:
            # Если формат неожиданный, пытаемся получить текст иначе
            ai_response = result.get("content", "").strip()
            if not ai_response:
                ai_response = json.dumps(result, ensure_ascii=False)
        
        logger.info(f"Получен ответ от Grok на сообщение: {user_message[:50]}...")
        return ai_response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при обращении к Grok API: {str(e)}")
        return "Произошла ошибка сети при обработке вашего запроса. Пожалуйста, попробуйте позже."
    except Exception as e:
        logger.error(f"Непредвиденная ошибка в AI client: {str(e)}")
        return "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."

def get_simple_response(user_message: str, knowledge_base: str) -> str:
    """
    Получает простой ответ от AI без использования истории диалога.
    Используется, например, для проверки, относится ли вопрос к компании.
    
    Args:
        user_message (str): Вопрос пользователя
        knowledge_base (str): Содержимое базы знаний о компании
        
    Returns:
        str: Ответ, сгенерированный AI
    """
    # Просто вызываем основную функцию с пустой историей
    return get_ai_response(user_message, knowledge_base, conversation_history=None)