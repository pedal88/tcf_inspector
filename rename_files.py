import json
import os
import shutil
from app.config import Config
from datetime import datetime

def rename_files():
    # Read current file
    current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
    if os.path.exists(current_file):
        with open(current_file, 'r') as f:
            data = json.load(f)
            version = data.get('vendorListVersion')
            gvl_version = data.get('gvlSpecificationVersion')
            tcf_version = data.get('tcfPolicyVersion')
            if all([version, gvl_version, tcf_version]):
                print(f'Current file has version {version}, GVL version {gvl_version}, and TCF version {tcf_version}')

    # Process archive files
    archive_dir = Config.ARCHIVE_DATA_DIR
    if os.path.exists(archive_dir):
        for filename in os.listdir(archive_dir):
            if filename.startswith('vendor_list_') and filename.endswith('.json'):
                filepath = os.path.join(archive_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    version = data.get('vendorListVersion')
                    gvl_version = data.get('gvlSpecificationVersion')
                    tcf_version = data.get('tcfPolicyVersion')
                    if all([version, gvl_version, tcf_version]):
                        new_filename = f'vendor_list_gvl{gvl_version}_tcf{tcf_version}_v{version}.json'
                        new_filepath = os.path.join(archive_dir, new_filename)
                        if filepath != new_filepath:
                            print(f'Renaming {filename} to {new_filename}')
                            shutil.move(filepath, new_filepath)

def rename_vendor_files():
    """Rename vendor list files to include the lastUpdated date at the beginning."""
    # Process files in archive directory
    archive_dir = Config.ARCHIVE_DATA_DIR
    
    for filename in os.listdir(archive_dir):
        if not (filename.endswith('.json') and 'vendor_list' in filename):
            continue
            
        file_path = os.path.join(archive_dir, filename)
        
        try:
            # Read the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Get the lastUpdated date
            last_updated = data.get('lastUpdated', '')
            if not last_updated:
                print(f"Warning: No lastUpdated date found in {filename}")
                continue
            
            # Parse the date (format: "2024-03-22T00:00:00Z")
            try:
                date_obj = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%SZ")
                date_str = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                print(f"Warning: Invalid date format in {filename}: {last_updated}")
                continue
            
            # Create new filename
            if not filename.startswith(date_str):
                new_filename = f"{date_str}_{filename}"
                new_path = os.path.join(archive_dir, new_filename)
                
                # Rename the file
                os.rename(file_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    # Process current file if it exists
    current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
    if os.path.exists(current_file):
        try:
            with open(current_file, 'r') as f:
                data = json.load(f)
            
            last_updated = data.get('lastUpdated', '')
            if last_updated:
                date_obj = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%SZ")
                date_str = date_obj.strftime("%Y-%m-%d")
                
                new_filename = f"{date_str}_current_vendor_list.json"
                new_path = os.path.join(Config.CURRENT_DATA_DIR, new_filename)
                
                # Create a copy with the date-prefixed name
                shutil.copy2(current_file, new_path)
                print(f"Created dated copy of current vendor list: {new_filename}")
        
        except Exception as e:
            print(f"Error processing current vendor list: {str(e)}")

if __name__ == '__main__':
    rename_vendor_files() 