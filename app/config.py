import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tcf_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # TCF API
    TCF_API_URL = 'https://vendor-list.consensu.org/v2/vendor-list.json'
    
    # File Storage
    CURRENT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'current')
    ARCHIVE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'archive')
    ARCHIVE_PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'archive_processed')
    VENDOR_METADATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'vendor_metadata')
    
    # Scheduler
    UPDATE_INTERVAL = timedelta(minutes=10)

    @staticmethod
    def init_app(app):
        # Create data directories if they don't exist
        os.makedirs(Config.CURRENT_DATA_DIR, exist_ok=True)
        os.makedirs(Config.ARCHIVE_DATA_DIR, exist_ok=True)
        os.makedirs(Config.ARCHIVE_PROCESSED_DIR, exist_ok=True)
        os.makedirs(Config.VENDOR_METADATA_DIR, exist_ok=True) 