from . import create_app
from src.utils.logger import get_logger

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

logger = get_logger("web.app")

@app.route("/")
def index():
    logger.info("Запрос к главной странице")
    return render_template("index.html")