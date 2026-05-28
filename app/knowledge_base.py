import json
import os

def load_knowledge_base(file_path="data/company_knowledge.json"):
    """
    Загружает базу знаний компании из JSON-файла.
    Если JSON не найден или повреждён, пробует запасные варианты.
    
    Args:
        file_path (str): Путь к файлу с базой знаний в JSON
        
    Returns:
        str: Текст базы знаний
    """
    try:
        # Сначала проверяем, существует ли файл JSON
        if not os.path.exists(file_path):
            # Если JSON нет, пробуем взять данные из Markdown (на всякий случай)
            markdown_path = "data/company_knowledge.md"
            if os.path.exists(markdown_path):
                with open(markdown_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                # Если и Markdown нет, возвращаем жёстко прописанные основные сведения
                return """Центр Красок #1 — казахстанский интернет-магазин и сеть офлайн-шоурумов лакокрасочных материалов, декоративных отделочных материалов и малярных инструментов. Компания работает в Алматы и Астане.

Юридическое лицо: ТОО SAMRUk Trade.
БИН: 140640024284.
Сайт: https://centr-krasok.kz/.
Email: info@centr-krasok.kz.
Основной телефон: +7 778 061 5000.
График работы: ежедневно с 10:00 до 20:00."""
        
        # Если файл JSON существует, пытаемся его распарсить
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Извлекаем поле с базой знаний, если оно есть
            return data.get("knowledge_base", "")
    except json.JSONDecodeError:
        # Если JSON оказался невалидным, пробуем прочитать файл как обычный текст (может, это Markdown)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception:
            # Если и это не удалось, возвращаем жёстко прописанные данные
            return """Центр Красок #1 — казахстанский интернет-магазин и сеть офлайн-шоурумов лакокрасочных материалов, декоративных отделочных материалов и малярных инструментов. Компания работает в Алматы и Астане.

Юридическое лицо: ТОО SAMRUk Trade.
БИН: 140640024284.
Сайт: https://centr-krasok.kz/.
Email: info@centr-krasok.kz.
Основной телефон: +7 778 061 5000.
График работы: ежедневно с 10:00 до 20:00."""
    except Exception as e:
        # Любая другая ошибка - бросаем исключение с пояснением
        raise Exception(f"Ошибка загрузки базы знаний: {str(e)}")