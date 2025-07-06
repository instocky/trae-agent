#!/usr/bin/env python3
"""
Тест Gemini API с использованием .env файла
Использует python-dotenv для загрузки переменных окружения
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

def load_environment():
    """Загружает переменные из .env файла"""
    # Ищем .env файл в корне проекта
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Загружен .env файл: {env_path}")
    else:
        print(f"⚠️  .env файл не найден: {env_path}")
        print("Создайте .env файл с GOOGLE_API_KEY")
        return False
    
    # Проверяем наличие API ключа
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY не найден в .env файле!")
        return False
    
    if api_key == 'your_google_gemini_api_key_here':
        print("❌ Замените GOOGLE_API_KEY на реальный ключ в .env файле!")
        return False
        
    print(f"✅ API ключ загружен: {api_key[:10]}...{api_key[-4:]}")
    return True

def test_gemini_with_env():
    """Тест Gemini API с настройками из .env"""
    
    if not load_environment():
        return False
    
    # Получаем настройки из .env
    api_key = os.getenv('GOOGLE_API_KEY')
    temperature = float(os.getenv('TEMPERATURE', 0.3))
    max_tokens = int(os.getenv('MAX_TOKENS', 4096))
    
    print(f"\n🔧 Настройки из .env:")
    print(f"   Temperature: {temperature}")
    print(f"   Max tokens: {max_tokens}")
    
    # Создаем клиент
    client = genai.Client(api_key=api_key)
    
    try:
        # Тест с рекомендуемой моделью
        print(f"\n🧪 Тестируем Gemini 2.5 Flash с настройками из .env")
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Привет! Расскажи в 2 предложениях, зачем нужны LLM агенты?',
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        
        print("✅ Тест успешен!")
        print(f"📝 Ответ: {response.text}")
        
        # Показываем метрики
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            print(f"\n📊 Метрики:")
            print(f"   Токены промпта: {response.usage_metadata.prompt_token_count}")
            print(f"   Токены ответа: {response.usage_metadata.candidates_token_count}")
            print(f"   Общее количество: {response.usage_metadata.total_token_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_env_variables():
    """Проверяем все переменные окружения"""
    
    print("\n🔍 Проверка всех переменных из .env:")
    
    env_vars = [
        'GOOGLE_API_KEY',
        'DEBUG', 
        'LOG_LEVEL',
        'DEFAULT_PROVIDER',
        'MAX_STEPS',
        'TEMPERATURE',
        'MAX_TOKENS'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'API_KEY' in var:
                # Скрываем API ключи
                display_value = f"{value[:6]}...{value[-4:]}"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: не установлена")

if __name__ == "__main__":
    print("🔍 Тестирование Gemini API с .env конфигурацией")
    print("=" * 60)
    
    success = test_gemini_with_env()
    test_env_variables()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 Все тесты пройдены! Gemini API готов к интеграции.")
    else:
        print("❌ Есть проблемы с конфигурацией. Проверьте .env файл.")
    
    print("\n💡 Следующий шаг: Изучение архитектуры провайдеров Trae Agent")
