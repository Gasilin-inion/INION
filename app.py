from flask import Flask, render_template, request, g
from src.utils.logger import get_logger # type: ignore
from routes.converter_routes import converter_bp # type: ignore
import time
import traceback
import os


app = Flask(__name__)
logger = get_logger("web.app")

# Регистрация blueprint с обработкой ошибок
try:
    app.register_blueprint(converter_bp, url_prefix='/converter')
    logger.info("Blueprint converter_bp успешно зарегистрирован")
except Exception as e:
    logger.error(f"Ошибка при регистрации blueprint: {e}")
    raise

# Middleware для логирования всех запросов
@app.before_request
def log_request_start():
    """Логирование начала запроса"""
    g.start_time = time.time()
    logger.info(f"Запрос начат: {request.method} {request.path} - IP: {request.remote_addr}")

@app.after_request
def log_request_end(response):
    """Логирование завершения запроса"""
    duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0
    
    logger.info(
        f"Запрос завершен: {request.method} {request.path} - "
        f"Статус: {response.status_code} - "
        f"Длительность: {duration:.3f}с - "
        f"IP: {request.remote_addr}"
    )
    
    return response

@app.errorhandler(404)
def not_found_error(error):
    """Обработка ошибки 404"""
    logger.warning(f"Страница не найдена: {request.path} - IP: {request.remote_addr}")
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработка ошибки 500"""
    logger.error(
        f"Внутренняя ошибка сервера: {request.path} - "
        f"Ошибка: {error}\n{traceback.format_exc()}"
    )
    return render_template("500.html"), 500

@app.route("/")
def index():
    """Главная страница"""
    try:
        logger.info(f"Рендеринг главной страницы - User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Ошибка при рендеринге index.html: {e}\n{traceback.format_exc()}")
        return "Произошла ошибка при загрузке страницы", 500

# Функция для проверки шаблонов
def check_templates():
    """Проверка существования необходимых шаблонов"""
    template_dir = app.template_folder
    required_templates = ['index.html', '404.html', '500.html']
    
    if not os.path.exists(template_dir):
        logger.error(f"Директория шаблонов не найдена: {template_dir}")
        return False
    
    missing_templates = []
    for template in required_templates:
        template_path = os.path.join(template_dir, template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
            logger.warning(f"Шаблон не найден: {template_path}")
    
    if missing_templates:
        logger.warning(f"Отсутствуют шаблоны: {', '.join(missing_templates)}")
        return False
    
    logger.info("Все необходимые шаблоны найдены")
    return True

# Выполняем проверку шаблонов при старте (вместо before_first_request)
check_templates()

if __name__ == "__main__":
    try:
        logger.info("=" * 50)
        logger.info("Запуск Flask-приложения")
        logger.info(f"Режим отладки: {app.debug}")
        logger.info(f"Хост: 0.0.0.0, Порт: 5000")
        logger.info(f"Директория шаблонов: {app.template_folder}")
        logger.info("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске приложения: {e}\n{traceback.format_exc()}")
        raise