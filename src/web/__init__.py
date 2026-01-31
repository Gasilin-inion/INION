from flask import Flask

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config["SECRET_KEY"] = "dev-secret-key"  # заменить через .env

    from .routes.converter_routes import converter_bp

    app.register_blueprint(converter_bp)

    return app
