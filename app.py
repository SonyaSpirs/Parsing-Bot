import logging
import signal
import sys
from loader import BotLoader

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальная переменная для отслеживания запущенного бота
current_bot_instance = None

def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    print(f"\n🛑 Получен сигнал {signum}, останавливаю бота...")
    sys.exit(0)

def main():
    global current_bot_instance
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Проверяем, не запущен ли уже бот
    if current_bot_instance:
        print("❌ Бот уже запущен! Остановите предыдущий экземпляр.")
        return

    try:
        print("🚀 Запускаю IT News Bot...")
        
        # Загружаем и настраиваем бота
        bot_loader = BotLoader()
        application = bot_loader.load_bot()
        
        current_bot_instance = application
        
        logger.info("🤖 Бот запущен!")
        print("=" * 50)
        print("IT News Bot успешно запущен!")
        print("Команды: /start, /news, /test, /help")
        print("Для остановки нажмите Ctrl+C")
        print("=" * 50)

        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
    finally:
        current_bot_instance = None

if __name__ == "__main__":
    main()
