#!/usr/bin/env python3
"""
Отладочный тест для анализа полного response от Gemini API
"""

import os
import json
from google import genai
from google.genai import types

def debug_gemini_response():
    """Отладка полного response объекта"""
    
    # Используем ваш API ключ
    api_key = "AIzaSyDOVZYFiT4TAgqbhZSDKyOIymL_LtDkKHg"
    client = genai.Client(api_key=api_key)
    
    models_to_test = [
        'gemini-2.5-flash',
        'gemini-2.0-flash-001'
    ]
    
    for model in models_to_test:
        print(f"\n{'='*60}")
        print(f"🔍 ОТЛАДКА МОДЕЛИ: {model}")
        print(f"{'='*60}")
        
        try:
            response = client.models.generate_content(
                model=model,
                contents='Привет! Как дела?',
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=100,
                )
            )
            
            print(f"✅ Запрос выполнен успешно")
            print(f"\n📋 ТИП ОБЪЕКТА: {type(response)}")
            print(f"📋 АТРИБУТЫ ОБЪЕКТА: {dir(response)}")
            
            # Попробуем разные способы получения текста
            print(f"\n📝 response.text: {repr(response.text)}")
            
            # Проверим другие атрибуты
            if hasattr(response, 'candidates'):
                print(f"📝 response.candidates: {response.candidates}")
                if response.candidates:
                    candidate = response.candidates[0]
                    print(f"📝 first candidate: {candidate}")
                    print(f"📝 candidate attributes: {dir(candidate)}")
                    
                    if hasattr(candidate, 'content'):
                        print(f"📝 candidate.content: {candidate.content}")
                        if hasattr(candidate.content, 'parts'):
                            print(f"📝 candidate.content.parts: {candidate.content.parts}")
                            if candidate.content.parts:
                                part = candidate.content.parts[0]
                                print(f"📝 first part: {part}")
                                if hasattr(part, 'text'):
                                    print(f"📝 part.text: {repr(part.text)}")
            
            # Попробуем сериализовать весь объект
            try:
                # Конвертируем в dict если возможно
                if hasattr(response, 'to_dict'):
                    response_dict = response.to_dict()
                    print(f"\n📦 ПОЛНЫЙ RESPONSE (to_dict):")
                    print(json.dumps(response_dict, indent=2, ensure_ascii=False))
                elif hasattr(response, '__dict__'):
                    print(f"\n📦 ПОЛНЫЙ RESPONSE (__dict__):")
                    print(json.dumps(response.__dict__, indent=2, ensure_ascii=False, default=str))
                else:
                    print(f"\n📦 ПОЛНЫЙ RESPONSE (repr):")
                    print(repr(response))
            except Exception as serialize_error:
                print(f"❌ Ошибка сериализации: {serialize_error}")
                print(f"📦 ПОЛНЫЙ RESPONSE (str): {str(response)}")
            
        except Exception as e:
            print(f"❌ Ошибка для модели {model}: {e}")

if __name__ == "__main__":
    print("🔍 ОТЛАДКА GEMINI API RESPONSE")
    debug_gemini_response()
