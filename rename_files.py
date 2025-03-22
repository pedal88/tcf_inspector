import json
import os
import shutil
from app.config import Config

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

if __name__ == '__main__':
    rename_files() 