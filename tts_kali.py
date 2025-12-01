#!/usr/bin/env python3
import pyperclip
import subprocess
import argparse
import sys

class KaliTTS:
    def __init__(self):
        self.check_dependencies()
    
    def check_dependencies(self):
        """Проверяет наличие необходимых зависимостей"""
        # Проверяем espeak
        try:
            subprocess.run(['espeak', '--version'], 
                          capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Ошибка: espeak не установлен.")
            print("Установите: sudo apt install espeak")
            sys.exit(1)
        
        # Проверяем pyperclip
        try:
            import pyperclip
        except ImportError:
            print("Ошибка: pyperclip не найден.")
            print("Установите: sudo apt install python3-pyperclip")
            sys.exit(1)
    
    def get_selected_text(self):
        """Получает выделенный текст используя pyperclip"""
        try:
            # Pyperclip автоматически определяет способ доступа к буферу
            text = pyperclip.paste()
            if not text or text.strip() == "":
                print("Буфер обмена пуст или содержит только пробелы.")
                return None
            return text.strip()
        except Exception as e:
            print(f"Ошибка при чтении буфера обмена: {e}")
            # Пробуем альтернативные методы
            return self._fallback_get_text()
    
    def _fallback_get_text(self):
        """Альтернативные методы получения текста"""
        methods = [
            (['xclip', '-o', '-selection', 'primary'], "X11 primary selection"),
            (['xclip', '-o'], "X11 clipboard"),
            (['xsel', '-o', '--primary'], "XSel primary"),
        ]
        
        for cmd, desc in methods:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    print(f"Получено через {desc}")
                    return result.stdout.strip()
            except FileNotFoundError:
                continue
        
        return None
    
    def text_to_speech(self, text, **kwargs):
        """Преобразует текст в речь с помощью espeak"""
        voice = kwargs.get('voice', 'ru')
        speed = kwargs.get('speed', 160)
        pitch = kwargs.get('pitch', 50)
        amplitude = kwargs.get('amplitude', 100)
        
        # Формируем команду для espeak
        cmd = [
            'espeak',
            '-v', voice,
            '-s', str(speed),
            '-p', str(pitch),
            '-a', str(amplitude),
            '--',  # Разделитель для текста
            text
        ]
        
        # Если указан файл для сохранения
        output_file = kwargs.get('output')
        if output_file:
            cmd.insert(-1, '-w')
            cmd.insert(-1, output_file)
            print(f"✓ Аудио сохраняется в: {output_file}")
        
        try:
            print(f"Голос: {voice}, Скорость: {speed}, Тон: {pitch}")
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Ошибка espeak: {e}")
            return False
    
    def list_voices(self):
        """Показывает доступные голоса"""
        try:
            result = subprocess.run(['espeak', '--voices'],
                                   capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            print("Доступные голоса:")
            print("-" * 50)
            for line in lines[1:]:  # Пропускаем заголовок
                parts = line.split()
                if len(parts) >= 4:
                    lang_code = parts[1]
                    voice_name = ' '.join(parts[3:])
                    print(f"{lang_code:8} - {voice_name}")
        except Exception as e:
            print(f"Не удалось получить список голосов: {e}")
    
    def get_available_voices(self):
        """Возвращает список доступных языковых кодов"""
        try:
            result = subprocess.run(['espeak', '--voices'],
                                   capture_output=True, text=True)
            voices = []
            for line in result.stdout.strip().split('\n')[1:]:
                parts = line.split()
                if parts:
                    voices.append(parts[1])
            return sorted(set(voices))
        except:
            return ['ru', 'en', 'de', 'fr', 'es']

def main():
    parser = argparse.ArgumentParser(
        description='TTS для Kali Linux - озвучка выделенного текста',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  tts                         # Озвучить выделенный текст
  tts -v en -s 200           # Английский голос, скорость 200
  tts -o речь.wav            # Сохранить в файл
  tts -l                     # Показать доступные голоса
  tts -t "Привет мир"        # Озвучить конкретный текст
  tts -v ru -s 120 -p 60    # Русский, медленно, высокий тон
        """
    )
    
    parser.add_argument('-v', '--voice', default='ru',
                       help='Язык/голос (ru, en, de и т.д.)')
    parser.add_argument('-s', '--speed', type=int, default=160,
                       help='Скорость речи (80-260, по умолчанию 160)')
    parser.add_argument('-p', '--pitch', type=int, default=50,
                       help='Тон голоса (0-99, по умолчанию 50)')
    parser.add_argument('-a', '--amplitude', type=int, default=100,
                       help='Громкость (0-200, по умолчанию 100)')
    parser.add_argument('-o', '--output',
                       help='Сохранить в WAV файл')
    parser.add_argument('-l', '--list-voices', action='store_true',
                       help='Показать доступные голоса')
    parser.add_argument('-t', '--text',
                       help='Текст для озвучки (если не указан, берет из буфера)')
    parser.add_argument('--test', action='store_true',
                       help='Тестовый режим (проверить работу)')
    
    args = parser.parse_args()
    
    tts = KaliTTS()
    
    if args.list_voices:
        tts.list_voices()
        return
    
    if args.test:
        print("=== ТЕСТОВЫЙ РЕЖИМ ===")
        print("1. Проверка зависимостей... ✓")
        print("2. Проверка доступных голосов...")
        
        voices = tts.get_available_voices()
        print(f"   Доступно голосов: {len(voices)}")
        print(f"   Примеры: {', '.join(voices[:5])}")
        
        test_text = "Тест работы TTS системы"
        print(f"3. Тест озвучки: '{test_text}'")
        
        tts.text_to_speech(test_text, voice='ru', speed=160)
        return
    
    # Получаем текст
    if args.text:
        text = args.text
        print(f"Текст из аргументов: {text[:100]}...")
    else:
        print("⌛ Получаю выделенный текст...")
        text = tts.get_selected_text()
        
        if not text:
            print("""
            Не удалось получить текст!
            
            Что делать:
            1. Выделите текст в любом приложении
            2. Запустите снова: tts
            3. Или укажите текст: tts -t "Ваш текст"
            """)
            sys.exit(1)
    
    if len(text) > 1000:
        print(f"⚠ Внимание: Текст очень длинный ({len(text)} символов)")
        confirm = input("Продолжить? (y/N): ")
        if confirm.lower() != 'y':
            print("Отменено.")
            return
    
    print(f"✓ Текст получен: {len(text)} символов")
    print(f"   Начало: {text[:150]}...")
    
    # Озвучиваем
    print("\n🎤 Начинаю озвучку...")
    success = tts.text_to_speech(
        text,
        voice=args.voice,
        speed=args.speed,
        pitch=args.pitch,
        amplitude=args.amplitude,
        output=args.output
    )
    
    if success:
        if args.output:
            print(f"\n✅ Готово! Аудиофайл сохранен: {args.output}")
        else:
            print("\n✅ Озвучка завершена!")
    else:
        print("\n❌ Ошибка при озвучке")

if __name__ == '__main__':
    main()
