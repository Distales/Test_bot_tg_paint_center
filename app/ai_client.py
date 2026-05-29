import logging
import requests
import json
from typing import List, Dict, Optional
from .config import GEMINI_API_KEY, GEMINI_MODEL
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
    Получает ответ от Gemini API (Google) на основе сообщения пользователя, базы знаний и истории диалога.
    
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
        # Формируем системную инструкцию, объединяя системный промпт и базу знаний
        system_instruction = {
            "parts": [{
                "text": f"{SYSTEM_PROMPT}\n\nБаза знаний о компании:\n\n{knowledge_base}"
            }]
        }
        
        # Формируем список contenов для Gemini API
        contents = []
        
        # Если есть история диалога, добавляем её
        if conversation_history:
            for msg in conversation_history:
                # Преобразуем роли: assistant -> model, user остается user
                role = msg["role"]
                if role == "assistant":
                    role = "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
        
        # Добавляем текущее сообщение пользователя
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })
        
        # Gemini API endpoint
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        headers = {
            "x-goog-api-key": GEMINI_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "systemInstruction": system_instruction,
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        # Выполняем запрос
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return "Произошла ошибка при обращении к AI API. Пожалуйста, попробуйте позже."
        
        # Парсим ответ
        result = response.json()
        # Извлекаем текст ответа
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                if parts and "text" in parts[0]:
                    ai_response = parts[0]["text"].strip()
                else:
                    ai_response = ""
            else:
                ai_response = ""
        else:
            ai_response = ""
        
        if not ai_response:
            # Если формат неожиданный, возвращаем пустой ответ или логгируем
            logger.warning(f"Unexpected Gemini API response format: {result}")
            ai_response = "Извините, не удалось получить ответ от AI."
        
        logger.info(f"Получен ответ от Gemini на сообщение: {user_message[:50]}...")
        return ai_response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при обращении к Gemini API: {str(e)}")
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