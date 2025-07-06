#!/usr/bin/env python3
"""
Тестовый файл для проверки Google Gemini API
Использует ваш API ключ от https://aistudio.google.com/apikey
"""

import os
from google import genai
from google.genai import types

def test_gemini_basic():
    """Базовый тест подключения к Gemini API"""
    
    # ВАЖНО: Замените 'YOUR_API_KEY' на ваш реальный API ключ
    api_key = "AIzaSyDOVZYFiT4TAgqbhZSDKyOIymL_LtDkKHg"  # Вставьте сюда ваш API ключ из Google AI Studio
    
    # Создаем клиент для Gemini Developer API
    client = genai.Client(api_key=api_key)
    
    try:
        # Простой тест генерации текста
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents='Привет! Напиши короткое стихотворение про Python.',
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=100,
            )
        )
        
        print("✅ Подключение к Gemini API успешно!")
        print(f"Ответ модели:\n{response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к Gemini API: {e}")
        return False

def test_gemini_with_config():
    """Тест с различными конфигурациями"""
    
    api_key = "AIzaSyDOVZYFiT4TAgqbhZSDKyOIymL_LtDkKHg"  # Вставьте сюда ваш API ключ
    client = genai.Client(api_key=api_key)
    
    try:
        # Тест с системными инструкциями
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents='Что такое LLM агенты?',
            config=types.GenerateContentConfig(
                system_instruction='Ты эксперт по искусственному интеллекту. Отвечай кратко и технически точно.',
                temperature=0.3,
                max_output_tokens=150,
            )
        )
        
        print("✅ Тест с конфигурацией успешен!")
        print(f"Ответ с системной инструкцией:\n{response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте с конфигурацией: {e}")
        return False

def test_gemini_models():
    """Тест доступных моделей"""
    
    api_key = "AIzaSyDOVZYFiT4TAgqbhZSDKyOIymL_LtDkKHg"  # Вставьте сюда ваш API ключ
    client = genai.Client(api_key=api_key)
    
    try:
        # Попробуем разные модели (включая новую 2.5 Flash)
        models_to_test = [
            'gemini-2.5-flash',           # Новая лучшая модель для агентов
            'gemini-2.5-flash-preview-05-20',  # Preview версия
            'gemini-2.0-flash-001',       # Предыдущая версия
            'gemini-1.5-flash',           # Старая версия
        ]
        
        for model in models_to_test:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents='Скажи "Привет" на трех языках.',
                    config=types.GenerateContentConfig(max_output_tokens=50)
                )
                print(f"✅ Модель {model}: работает")
                # Безопасная обработка response.text
                answer = response.text.strip() if response.text else "Ответ пустой"
                print(f"   Ответ: {answer}")
                
            except Exception as model_error:
                print(f"❌ Модель {model}: {model_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Общая ошибка тестирования моделей: {e}")
        return False

def test_gemini_agent_capabilities():
    """Тест агентных возможностей Gemini 2.5 Flash"""
    
    api_key = "YOUR_API_KEY"  # Вставьте сюда ваш API ключ
    client = genai.Client(api_key=api_key)
    
    try:
        # Тест структурированного вывода (важно для агентов)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Проанализируй задачу: "Создать Python скрипт для работы с файлами". Разбей на подзадачи.',
            config=types.GenerateContentConfig(
                system_instruction='''Ты помощник разработчика. Анализируй задачи и разбивай их на конкретные шаги.
                Отвечай в формате:
                1. Подзадача 1
                2. Подзадача 2
                3. ...''',
                temperature=0.1,  # Низкая температура для консистентности
                max_output_tokens=200,
            )
        )
        
        print("✅ Тест агентных возможностей успешен!")
        print(f"Анализ задачи:\n{response.text}")
        
        # Тест мышления (thinking) - новая возможность
        response2 = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Объясни пошагово, как создать простой веб-сервер на Python',
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=300,
            )
        )
        
        print("\n✅ Тест пошагового мышления:")
        print(f"{response2.text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте агентных возможностей: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Тестирование Google Gemini API")
    print("=" * 50)
    
    print("\n1. Базовый тест подключения:")
    test_gemini_basic()
    
    print("\n2. Тест с конфигурацией:")
    test_gemini_with_config()
    
    print("\n3. Тест доступных моделей:")
    test_gemini_models()
    
    print("\n4. Тест агентных возможностей (Gemini 2.5 Flash):")
    test_gemini_agent_capabilities()
    
    print("\n" + "=" * 50)
    print("📝 Инструкции:")
    print("1. Замените 'YOUR_API_KEY' на ваш реальный API ключ")
    print("2. API ключ можно получить здесь: https://aistudio.google.com/apikey")
    print("3. Запустите: python test_gemini.py")
    print("4. Gemini 2.5 Flash - лучшая модель для агентов!")
