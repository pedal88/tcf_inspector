import os
import json
from datetime import datetime
from app.config import Config

class FileManager:
    @staticmethod
    def save_current_data(data):
        """Save data to current directory"""
        os.makedirs(Config.CURRENT_DATA_DIR, exist_ok=True)
        current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
        
        with open(current_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    @staticmethod
    def save_archive_data(data):
        """Save data to archive directory with timestamp"""
        os.makedirs(Config.ARCHIVE_DATA_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_file = os.path.join(Config.ARCHIVE_DATA_DIR, f'vendor_list_{timestamp}.json')
        
        with open(archive_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return archive_file
    
    @staticmethod
    def get_current_data():
        """Get current vendor list data"""
        current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
        if not os.path.exists(current_file):
            return None
            
        with open(current_file, 'r') as f:
            return json.load(f)
            
    @staticmethod
    def get_archive_files():
        """Get list of archive files sorted by date"""
        if not os.path.exists(Config.ARCHIVE_DATA_DIR):
            return []
            
        files = [f for f in os.listdir(Config.ARCHIVE_DATA_DIR) 
                if f.startswith('vendor_list_') and f.endswith('.json')]
        return sorted(files, reverse=True)
    
    @staticmethod
    def get_archive_data(filename):
        """Get specific archive data"""
        archive_file = os.path.join(Config.ARCHIVE_DATA_DIR, filename)
        if not os.path.exists(archive_file):
            return None
            
        with open(archive_file, 'r') as f:
            return json.load(f) 