# Gemini Provider Implementation Details

## 🔧 Текущее состояние реализации

**Дата:** 06 июля 2025  
**Статус:** В процессе отладки function calling  
**Прогресс:** 90% - основная функциональность работает, остались проблемы с инструментами

## ✅ Что работает

### API Интеграция
- ✅ **Подключение к Gemini API** - успешно через google-genai SDK
- ✅ **Аутентификация** - API ключ из .env или config с fallback
- ✅ **Генерация текста** - базовые запросы работают корректно
- ✅ **Системные инструкции** - через system_instruction параметр
- ✅ **Токены и метрики** - usage_metadata корректно маппится на LLMUsage
- ✅ **Траектория** - record_llm_interaction работает

### Архитектурная интеграция
- ✅ **BaseLLMClient** - все абстрактные методы реализованы
- ✅ **LLMProvider.GEMINI** - добавлен в enum
- ✅ **LLMClient** - автоматический импорт GeminiClient
- ✅ **Конфигурация** - trae_config.json поддерживает gemini провайдера

### Trae Agent Интеграция
- ✅ **Step 1 выполняется** - agent может думать и планировать
- ✅ **Lakeview summaries** - генерируются корректно
- ✅ **Токены подсчитываются** - input/output/total tokens
- ✅ **Траектория записывается** - trajectory.json содержит данные

## ❌ Известные проблемы

### Function Calling Issues

#### 1. **Неправильные имена инструментов**
```
Gemini вызывает: "sequential_thinking" 
Доступно в Trae:  "sequentialthinking"
```
**Проблема:** Gemini не следует точным именам инструментов из schema

#### 2. **Function Response Format**
```
Ошибка: "Please ensure that function response turn comes immediately after a function call turn"
```
**Статус:** Частично исправлено с правильными ролями, но может требовать дополнительной отладки

#### 3. **Tool Result Processing**
```python
# Текущая реализация:
name=message.tool_result.call_id.replace("call_", "") if message.tool_result.call_id else "unknown"

# Проблема: ToolResult не содержит original function name
```

## 📊 Архитектурные выводы

### Структура запроса к Gemini
```python
response = self.client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[types.Content(role="user|model", parts=[...])],
    config=types.GenerateContentConfig(
        system_instruction="...",  # Отдельный параметр
        tools=[types.Tool(function_declarations=[...])],
        temperature=0.3,
        max_output_tokens=4096,
        top_p=1.0,
        top_k=40
    )
)
```

### Маппинг ролей для Gemini
```python
LLM Message Role → Gemini Role
"system"    → system_instruction (отдельный параметр)
"user"      → "user" 
"assistant" → "model"

Function Call  → role="model" (всегда от модели)
Function Response → role="user" (всегда к модели)
```

### Маппинг токенов
```python
Gemini → LLMUsage
response.usage_metadata.prompt_token_count → input_tokens
response.usage_metadata.candidates_token_count → output_tokens  
response.usage_metadata.thoughts_token_count → reasoning_tokens (уникально для Gemini 2.5)
response.usage_metadata.total_token_count → НЕ ИСПОЛЬЗУЕТСЯ (считаем сами)
```

### Tool Schema Conversion
```python
# Trae Agent Tool Schema → Gemini Schema
JSON Schema type mapping:
"string" → "STRING"
"integer" → "INTEGER" 
"number" → "NUMBER"
"boolean" → "BOOLEAN"
"array" → "ARRAY"
"object" → "OBJECT"

# Метод конвертации:
tool.get_input_schema() → types.Schema via _convert_tool_schema()
```

## 🔧 Критические методы

### 1. **API Key Resolution**
```python
def __init__(self, model_parameters: ModelParameters):
    # Обязательная проверка placeholder
    if self.api_key == "" or self.api_key == "your_google_api_key":
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if self.api_key == "" or self.api_key == "your_google_api_key":
        raise ValueError("Google API key not provided...")
```

### 2. **Message Parsing** 
```python
def chat(self, messages: list[LLMMessage], ...):
    system_instruction = None
    contents = []
    
    for message in messages:
        if message.role == "system":
            system_instruction = message.content
        elif message.role in ["user", "assistant"]:
            # Конвертация в types.Content
```

### 3. **Response Parsing**
```python
def _parse_response(self, response: types.GenerateContentResponse, model: str):
    content = response.text if response.text else ""
    
    # Usage mapping
    usage = LLMUsage(
        input_tokens=usage_meta.prompt_token_count,
        output_tokens=usage_meta.candidates_token_count,
        reasoning_tokens=usage_meta.thoughts_token_count or 0  # Gemini 2.5 specific
    )
```

## 🚨 Нерешенные вопросы

### 1. **Function Name Resolution**
- **Проблема:** ToolResult не содержит original function name
- **Текущее решение:** Используем call_id.replace("call_", "")
- **Возможные улучшения:** 
  - Кэшировать маппинг call_id → function_name
  - Модифицировать ToolResult для хранения function_name

### 2. **Tool Schema Validation**
- **Вопрос:** Всегда ли корректно конвертируется complex JSON schema?
- **Тестирование:** Нужны тесты для nested objects, arrays, required fields

### 3. **Error Handling**
- **Function call errors** - как обрабатывать failed tool executions?
- **API rate limits** - retry logic?
- **Malformed responses** - fallback strategies?

## 📋 Следующие шаги для отладки

### Приоритет 1: Function Calling
1. **Исследовать tool name mapping**
   - Почему Gemini генерирует "sequential_thinking" вместо "sequentialthinking"
   - Возможно, проблема в description или schema

2. **Отладить function response format**
   - Проверить sequence: function_call → function_response
   - Убедиться в правильности role assignment

3. **Добавить детальное логирование**
   - Логировать все function calls/responses
   - Отслеживать conversation flow

### Приоритет 2: Стабилизация
1. **Comprehensive testing**
   - Тесты без инструментов (только текст)
   - Тесты с простыми инструментами
   - Тесты с комплексными workflows

2. **Error handling improvements**
   - Graceful degradation при function call errors
   - Retry mechanisms
   - Better error messages

## 💡 Оптимизации

### Performance
- **Кэширование** tool schemas
- **Batch requests** для множественных tool calls  
- **Streaming responses** для длинных ответов

### User Experience  
- **Better error messages** для configuration issues
- **Model recommendations** based on task type
- **Token usage warnings** для expensive operations

## 📚 Полезные референсы

### Gemini API Documentation
- [Function Calling Guide](https://ai.google.dev/gemini-api/docs/function-calling)
- [Content and Parts Structure](https://ai.google.dev/gemini-api/docs/vision)
- [Error Codes Reference](https://ai.google.dev/gemini-api/docs/error-codes)

### Trae Agent Architecture
- `trae_agent/utils/openai_client.py` - референс для function calling
- `trae_agent/utils/trajectory_recorder.py` - траектория записи
- `trae_agent/tools/base.py` - Tool, ToolCall, ToolResult structures

---

**Последнее обновление:** Step 2 error - function response format issue  
**Следующий тест:** Исправление ролей function_call/function_response
