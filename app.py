# app.py (в корневой директории)
from flask import Flask, render_template
from src.web.routes.converter_routes import converter_bp
from src.web.routes.api_routes import api_bp
from src.utils.logger import get_logger
from src.utils.config_loader import load_config
import os

# Создаем экземпляр приложения
app = Flask(__name__, 
            template_folder='src/web/templates',
            static_folder='src/web/static')

# Загружаем конфигурацию
app.config.update(load_config())

# Регистрируем blueprints
app.register_blueprint(converter_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# Настраиваем логирование
logger = get_logger("web.app")

@app.route("/")
def index():
    """Главная страница"""
    logger.info("Запрос к главной странице")
    return render_template("index.html")

@app.route("/health")
def health():
    """Проверка работоспособности"""
    return {"status": "ok"}, 200

# Обработчики ошибок
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Внутренняя ошибка сервера: {error}")
    return render_template("500.html"), 500

if __name__ == "__main__":
    # Получаем настройки из окружения или используем значения по умолчанию
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"Запуск приложения на {host}:{port} (debug={debug})")
    app.run(debug=debug, host=host, port=port)