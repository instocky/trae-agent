# Provider Architecture Analysis

## 🏗️ Архитектура провайдеров Trae Agent

### Общая структура

```
LLMClient (Facade)
    ↓
BaseLLMClient (Abstract Base Class)
    ↓
[OpenAIClient, AnthropicClient, AzureClient] (Concrete Implementations)
```

## 📋 Ключевые компоненты

### 1. **LLMProvider (Enum)**
```python
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    # 🎯 GEMINI = "gemini"  # Добавим здесь
```

### 2. **ModelParameters (Dataclass)**
```python
@dataclass
class ModelParameters:
    model: str                    # Название модели
    api_key: str                 # API ключ
    max_tokens: int              # Максимум токенов
    temperature: float           # Температура генерации
    top_p: float                 # Top-p параметр
    top_k: int                   # Top-k параметр  
    parallel_tool_calls: bool    # Параллельные вызовы инструментов
    max_retries: int             # Количество повторов
    base_url: str | None = None  # Базовый URL
    api_version: str | None = None # Версия API
```

### 3. **BaseLLMClient (ABC)**
Абстрактный базовый класс для всех провайдеров:

```python
class BaseLLMClient(ABC):
    def __init__(self, model_parameters: ModelParameters)
    
    # Обязательные методы для реализации:
    @abstractmethod
    def set_chat_history(self, messages: list[LLMMessage]) -> None
    
    @abstractmethod  
    def chat(self, messages: list[LLMMessage], model_parameters: ModelParameters, 
             tools: list[Tool] | None = None, reuse_history: bool = True) -> LLMResponse
    
    @abstractmethod
    def supports_tool_calling(self, model_parameters: ModelParameters) -> bool
```

## 📊 Структуры данных

### LLMMessage
```python
@dataclass
class LLMMessage:
    role: str                          # "system", "user", "assistant"
    content: str | None = None         # Текст сообщения
    tool_call: ToolCall | None = None  # Вызов инструмента
    tool_result: ToolResult | None = None # Результат инструмента
```

### LLMResponse  
```python
@dataclass
class LLMResponse:
    content: str                       # Основной ответ
    usage: LLMUsage | None = None      # Метрики токенов
    model: str | None = None           # Название модели
    finish_reason: str | None = None   # Причина завершения
    tool_calls: list[ToolCall] | None = None # Вызовы инструментов
```

### LLMUsage
```python
@dataclass  
class LLMUsage:
    input_tokens: int                  # Токены ввода
    output_tokens: int                 # Токены вывода
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    reasoning_tokens: int = 0          # Токены размышления
```

## 🔧 Паттерн реализации провайдера

### Пример: OpenAIClient

1. **Инициализация**
```python
def __init__(self, model_parameters: ModelParameters):
    super().__init__(model_parameters)
    
    # Получение API ключа из переменных окружения или параметров
    if self.api_key == "":
        self.api_key = os.getenv("OPENAI_API_KEY", "")
    
    # Создание клиента провайдера
    self.client = openai.OpenAI(api_key=self.api_key)
    self.message_history = []
```

2. **Преобразование сообщений**
```python
def parse_messages(self, messages: list[LLMMessage]) -> ProviderFormat:
    """Конвертация из LLMMessage в формат провайдера"""
    # Обработка tool_calls, tool_results, обычных сообщений
```

3. **Основной метод chat**
```python
def chat(self, messages: list[LLMMessage], model_parameters: ModelParameters, 
         tools: list[Tool] | None = None, reuse_history: bool = True) -> LLMResponse:
    
    # 1. Преобразование сообщений в формат провайдера
    provider_messages = self.parse_messages(messages)
    
    # 2. Подготовка схем инструментов (если есть)
    tool_schemas = self.prepare_tool_schemas(tools) if tools else None
    
    # 3. Вызов API провайдера
    response = self.client.chat.completions.create(
        model=model_parameters.model,
        messages=provider_messages,
        tools=tool_schemas,
        temperature=model_parameters.temperature,
        max_tokens=model_parameters.max_tokens
    )
    
    # 4. Преобразование ответа в LLMResponse
    return self.parse_response(response)
```

4. **Поддержка инструментов**
```python
def supports_tool_calling(self, model_parameters: ModelParameters) -> bool:
    """Проверка поддержки function calling для модели"""
    tool_capable_models = ["gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]
    return any(model in model_parameters.model for model in tool_capable_models)
```

## 🎯 План для Gemini Provider

### 1. Создать GeminiClient
```python
class GeminiClient(BaseLLMClient):
    def __init__(self, model_parameters: ModelParameters):
        super().__init__(model_parameters)
        
        # API ключ из env или параметров
        if self.api_key == "":
            self.api_key = os.getenv("GOOGLE_API_KEY", "")
            
        # Создание Google Gemini клиента
        self.client = genai.Client(api_key=self.api_key)
        self.message_history = []
```

### 2. Основные методы
- `parse_messages()` - конвертация LLMMessage → Gemini format
- `chat()` - основной метод с вызовом `client.models.generate_content()`
- `parse_response()` - конвертация Gemini response → LLMResponse
- `supports_tool_calling()` - поддержка function calling

### 3. Интеграция в LLMClient
```python
# В llm_client.py
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic" 
    AZURE = "azure"
    GEMINI = "gemini"  # ✨ Добавить

# В конструкторе LLMClient
elif provider == LLMProvider.GEMINI:
    from .gemini_client import GeminiClient
    self.client = GeminiClient(model_parameters)
```

## 🔍 Особенности для Gemini

### Преимущества
- **Структурированный SDK**: `google-genai` уже предоставляет Pydantic модели
- **Совместимость**: Gemini response легко мапится на LLMUsage
- **Function Calling**: Полная поддержка инструментов
- **Мультимодальность**: Поддержка изображений/видео (для будущего)

### Вызовы
- **Формат сообщений**: Нужно адаптировать `role` систему (user/assistant/model)
- **System Instructions**: Gemini использует отдельный параметр
- **Токены thinking**: Специфичные для Gemini 2.5 Flash

## 📁 Файлы для создания

1. `trae_agent/utils/gemini_client.py` - Основная реализация
2. Обновить `trae_agent/utils/llm_client.py` - Добавить GEMINI провайдер
3. Обновить конфигурацию - Добавить Gemini настройки в `trae_config.json`
4. Тесты интеграции - Проверить работу с Trae Agent

## ✅ Готовность к реализации

- ✅ **API протестирован** - Gemini работает стабильно
- ✅ **Архитектура изучена** - Паттерн понятен
- ✅ **Структуры данных** - Совместимость подтверждена
- ✅ **Инфраструктура** - .env и тесты готовы

**Следующий шаг:** Реализация `GeminiClient` по образцу `OpenAIClient`
