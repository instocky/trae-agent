#!/usr/bin/env python3
"""
Тестовый файл для Gemini API с использованием переменной окружения
Использует GOOGLE_API_KEY из переменных окружения
"""

import os
from google import genai
from google.genai import types

def get_api_key():
    """Получает API ключ из переменной окружения или спрашивает у пользователя"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Переменная окружения GOOGLE_API_KEY не найдена!")
        print("Установите её командой:")
        print('set GOOGLE_API_KEY=ваш_api_ключ')
        print("\nИли введите API ключ сейчас:")
        api_key = input("API ключ: ").strip()
        if not api_key:
            raise ValueError("API ключ не предоставлен!")
    return api_key

def test_gemini_25_flash():
    """Тест новой модели Gemini 2.5 Flash"""
    
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    
    print("🧪 Тестируем Gemini 2.5 Flash - лучшую модель для агентов")
    
    try:
        # Тест базовой генерации
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Объясни в 3 предложениях, что такое LLM агенты.',
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=150,
            )
        )
        
        print("✅ Gemini 2.5 Flash работает отлично!")
        text = response.text if response.text else "Пустой ответ"
        print(f"Ответ: {text}")
        
        # Тест структурированного вывода
        response2 = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Создай план изучения Python за неделю. Ответь списком из 7 дней.',
            config=types.GenerateContentConfig(
                system_instruction='Отвечай четким списком по дням. День 1:..., День 2:...',
                temperature=0.1,
                max_output_tokens=200,
            )
        )
        
        print("\n✅ Структурированный вывод:")
        text2 = response2.text if response2.text else "Пустой ответ"
        print(f"{text2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_models_comparison():
    """Сравнение моделей Gemini"""
    
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    
    models = [
        'gemini-2.5-flash',
        'gemini-2.0-flash-001', 
        'gemini-1.5-flash'
    ]
    
    prompt = "Напиши функцию Python для сортировки списка"
    
    print("\n🔍 Сравнение моделей Gemini:")
    
    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=100,
                )
            )
            
            text = response.text if response.text else "Пустой ответ"
            print(f"\n✅ {model}:")
            print(f"   {text[:100]}...")
            
        except Exception as e:
            print(f"\n❌ {model}: {str(e)[:100]}...")

if __name__ == "__main__":
    print("🔍 Тестирование Gemini 2.5 Flash для агентов")
    print("=" * 60)
    
    try:
        test_gemini_25_flash()
        test_models_comparison()
        
        print(f"\n{'='*60}")
        print("🎉 Тестирование завершено!")
        print("💡 Рекомендация: Используйте gemini-2.5-flash для Trae Agent")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("\n📝 Убедитесь что:")
        print("1. Установлена переменная GOOGLE_API_KEY")
        print("2. API ключ валидный")
        print("3. Есть интернет соединение")
