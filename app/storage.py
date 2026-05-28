class ConversationStorage:
    def __init__(self, max_messages=5):
        """
        Инициализирует хранилище истории диалогов.
        
        Args:
            max_messages (int): Сколько последних сообщений хранить для каждого пользователя
        """
        self.max_messages = max_messages
        self.storage = {}  # Словарь: user_id -> список сообщений
    
    def add_message(self, user_id, role, content):
        """
        Добавляет сообщение в историю диалога конкретного пользователя.
        
        Args:
            user_id (int): Идентификатор пользователя в Telegram
            role (str): Роль отправителя - 'user' или 'assistant'
            content (str): Текст сообщения
        """
        # Если для этого пользователя ещё нет записи в словаре - создаём пустой список
        if user_id not in self.storage:
            self.storage[user_id] = []
        
        # Добавляем сообщение в конец списка
        self.storage[user_id].append({"role": role, "content": content})
        
        # Оставляем только последние max_messages сообщений, удаляя старые
        if len(self.storage[user_id]) > self.max_messages:
            self.storage[user_id] = self.storage[user_id][-self.max_messages:]
    
    def get_history(self, user_id):
        """
        Возвращает полную историю диалога для указанного пользователя.
        
        Args:
            user_id (int): Идентификатор пользователя в Telegram
            
        Returns:
            list: Список словарей с ключами 'role' и 'content'
        """
        # Если пользователя нет в словаре - возвращаем пустой список
        return self.storage.get(user_id, [])
    
    def clear_history(self, user_id):
        """
        Очищает всю историю диалога для указанного пользователя.
        
        Args:
            user_id (int): Идентификатор пользователя в Telegram
        """
        # Если пользователь есть в словаре - удаляем его запись
        if user_id in self.storage:
            del self.storage[user_id]
    
    def get_formatted_history(self, user_id):
        """
        Возвращает отформатированную строку истории диалога для передачи в AI.
        Формат: "Роль: Текст сообщения" с переносами строк.
        
        Args:
            user_id (int): Идентификатор пользователя в Telegram
            
        Returns:
            str: Отформатированная история диалога
        """
        history = self.get_history(user_id)
        if not history:
            return ""
        
        formatted_lines = []
        for msg in history:
            # Определяем русское название роли для лучшей читаемости в промпте
            role_name = "Пользователь" if msg["role"] == "user" else "Ассистент"
            formatted_lines.append(f"{role_name}: {msg['content']}")
        
        # Соединяем все строки переносом строки
        return "\n".join(formatted_lines)