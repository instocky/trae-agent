#!/usr/bin/env python3
"""
Тест интеграции Gemini провайдера с Trae Agent
Проверяет работу GeminiClient в рамках архитектуры Trae Agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавим путь к trae_agent для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from trae_agent.utils.llm_client import LLMClient, LLMProvider
from trae_agent.utils.config import ModelParameters
from trae_agent.utils.llm_basics import LLMMessage, LLMResponse


def load_environment():
    """Загружает переменные из .env файла"""
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Загружен .env файл: {env_path}")
    else:
        print(f"⚠️  .env файл не найден: {env_path}")
        return False
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_google_gemini_api_key_here':
        print("❌ GOOGLE_API_KEY не найден или не настроен в .env файле!")
        return False
        
    print(f"✅ API ключ загружен: {api_key[:10]}...{api_key[-4:]}")
    return True


def test_gemini_provider_integration():
    """Тест интеграции Gemini провайдера"""
    
    print("🧪 Тестируем интеграцию Gemini провайдера с Trae Agent")
    
    # Настройки модели из .env
    model_params = ModelParameters(
        model="gemini-2.5-flash",
        api_key=os.getenv('GOOGLE_API_KEY', ''),
        max_tokens=int(os.getenv('MAX_TOKENS', 4096)),
        temperature=float(os.getenv('TEMPERATURE', 0.3)),
        top_p=1.0,
        top_k=40,
        parallel_tool_calls=True,
        max_retries=3
    )
    
    try:
        # Создаем LLMClient с Gemini провайдером
        llm_client = LLMClient(
            provider=LLMProvider.GEMINI,
            model_parameters=model_params
        )
        
        print(f"✅ LLMClient создан с провайдером: {llm_client.provider}")
        
        # Тест 1: Простое сообщение
        print("\n📝 Тест 1: Простое сообщение")
        messages = [
            LLMMessage(role="user", content="Привет! Как дела? Ответь в 2 предложениях.")
        ]
        
        response: LLMResponse = llm_client.chat(
            messages=messages,
            model_parameters=model_params
        )
        
        print(f"✅ Ответ получен: {response.content}")
        print(f"📊 Модель: {response.model}")
        print(f"📊 Finish reason: {response.finish_reason}")
        
        if response.usage:
            print(f"📊 Токены: вход={response.usage.input_tokens}, выход={response.usage.output_tokens}")
            if response.usage.reasoning_tokens > 0:
                print(f"📊 Токены размышления: {response.usage.reasoning_tokens}")
        
        # Тест 2: С системной инструкцией
        print("\n📝 Тест 2: Системная инструкция")
        messages_with_system = [
            LLMMessage(role="system", content="Ты помощник программиста. Отвечай кратко и технически точно."),
            LLMMessage(role="user", content="Что такое dependency injection в Python?")
        ]
        
        response2 = llm_client.chat(
            messages=messages_with_system,
            model_parameters=model_params
        )
        
        print(f"✅ Ответ с системной инструкцией: {response2.content[:100]}...")
        
        # Тест 3: Проверка поддержки function calling
        print("\n📝 Тест 3: Поддержка function calling")
        supports_tools = llm_client.client.supports_tool_calling(model_params)
        print(f"✅ Function calling поддерживается: {supports_tools}")
        
        # Тест 4: Множественные сообщения (диалог)
        print("\n📝 Тест 4: Диалог")
        dialog_messages = [
            LLMMessage(role="user", content="Напиши простую функцию Python для сложения двух чисел"),
            LLMMessage(role="assistant", content="def add(a, b):\n    return a + b"),
            LLMMessage(role="user", content="Добавь проверку типов")
        ]
        
        response3 = llm_client.chat(
            messages=dialog_messages,
            model_parameters=model_params
        )
        
        print(f"✅ Ответ в диалоге: {response3.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_enum():
    """Тест корректности LLMProvider enum"""
    
    print("\n🔍 Проверка LLMProvider enum")
    
    # Проверим что GEMINI добавлен в enum
    try:
        gemini_provider = LLMProvider.GEMINI
        print(f"✅ LLMProvider.GEMINI: {gemini_provider.value}")
        
        # Проверим создание из строки
        gemini_from_string = LLMProvider("gemini")
        print(f"✅ LLMProvider('gemini'): {gemini_from_string.value}")
        
        # Список всех провайдеров
        all_providers = [provider.value for provider in LLMProvider]
        print(f"✅ Все провайдеры: {all_providers}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в LLMProvider: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Тестирование интеграции Gemini провайдера")
    print("=" * 60)
    
    # Загрузка окружения
    if not load_environment():
        print("❌ Не удалось загрузить окружение")
        sys.exit(1)
    
    # Тест enum
    enum_success = test_provider_enum()
    
    # Тест интеграции
    integration_success = test_gemini_provider_integration()
    
    print(f"\n{'='*60}")
    if enum_success and integration_success:
        print("🎉 Все тесты интеграции пройдены!")
        print("✅ Gemini провайдер успешно интегрирован в Trae Agent")
        print("\n💡 Можно использовать: trae-cli run 'ваша задача' --provider gemini")
    else:
        print("❌ Есть проблемы с интеграцией")
        print("🔧 Проверьте зависимости и конфигурацию")
