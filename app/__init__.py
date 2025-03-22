from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import Config

db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    
    from app.views.main import main_bp
    app.register_blueprint(main_bp)

    # Initialize scheduler for data updates
    from app.services.scheduler import schedule_data_updates
    scheduler.start()
    schedule_data_updates()

    return app 