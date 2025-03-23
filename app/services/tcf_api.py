import requests
import json
import os
from datetime import datetime
from app.config import Config

class TCFAPIService:
    BASE_URL = "https://vendor-list.consensu.org/v3"
    CURRENT_LIST_URL = f"{BASE_URL}/vendor-list.json"
    ARCHIVE_URL_TEMPLATE = f"{BASE_URL}/archives/vendor-list-v{{version}}.json"

    @staticmethod
    def get_filename(data):
        """Generate filename based on GVL spec version, TCF policy version, and vendor list version"""
        gvl_version = data.get('gvlSpecificationVersion')
        tcf_version = data.get('tcfPolicyVersion')
        version = data.get('vendorListVersion')
        
        if not all([gvl_version, tcf_version, version]):
            raise ValueError("Missing required version information in data")
            
        return f'vendor_list_gvl{gvl_version}_tcf{tcf_version}_v{version}.json'

    @staticmethod
    def parse_filename(filename):
        """Parse version information from filename"""
        try:
            # Extract versions from filename like vendor_list_gvl2_tcf2_v223.json
            import re
            match = re.match(r'vendor_list_gvl(\d+)_tcf(\d+)_v(\d+)\.json', filename)
            if match:
                return {
                    'gvl_version': int(match.group(1)),
                    'tcf_version': int(match.group(2)),
                    'version': int(match.group(3))
                }
        except Exception:
            pass
        return None

    @staticmethod
    def get_current_version():
        """Fetch the current vendor list to get its version number"""
        try:
            response = requests.get(TCFAPIService.CURRENT_LIST_URL)
            response.raise_for_status()
            data = response.json()
            return data.get('vendorListVersion')
        except requests.RequestException as e:
            print(f"Error fetching current version: {e}")
            return None

    @staticmethod
    def get_stored_version():
        """Get the version number from the current version file"""
        version_file = os.path.join(Config.CURRENT_DATA_DIR, 'version.txt')
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                try:
                    return int(f.read().strip())
                except ValueError:
                    return None
        return None

    @staticmethod
    def fetch_vendor_list(version=None):
        """Fetch vendor list for specific version or current if version is None"""
        try:
            if version:
                url = TCFAPIService.ARCHIVE_URL_TEMPLATE.format(version=version)
            else:
                url = TCFAPIService.CURRENT_LIST_URL

            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching vendor list: {e}")
            return None

    @staticmethod
    def process_vendor_list_file(file_path):
        """Process a vendor list file using the process_current_gvl.py script"""
        try:
            import subprocess
            result = subprocess.run(['./process_current_gvl.py', file_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully processed vendor list file: {file_path}")
                return True
            else:
                print(f"Error processing vendor list file: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error running process script: {e}")
            return False

    @staticmethod
    def save_to_archive_only(data):
        """Save vendor list data directly to archive without affecting current version"""
        if not data:
            print("No data provided to save")
            return False

        try:
            # Generate filename with both versions
            archive_file = os.path.join(Config.ARCHIVE_DATA_DIR, TCFAPIService.get_filename(data))
            
            # Ensure archive directory exists
            os.makedirs(Config.ARCHIVE_DATA_DIR, exist_ok=True)

            # Check if this version already exists in archive
            if os.path.exists(archive_file):
                print(f"File {os.path.basename(archive_file)} already exists in archive, skipping")
                return False

            # Save to archive
            with open(archive_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Successfully archived {os.path.basename(archive_file)}")
            
            # Process the archived file
            TCFAPIService.process_vendor_list_file(archive_file)
            
            return True

        except Exception as e:
            print(f"Error saving to archive: {e}")
            return False

    @staticmethod
    def save_vendor_list(data):
        """Save vendor list data and archive if it's a new version, never overwrite with older data"""
        if not data:
            print("No data provided to save")
            return False

        try:
            # Get version from the new data
            new_version = data.get('vendorListVersion')
            if not new_version:
                print("No version number in vendor list data")
                return False

            new_version = int(new_version)

            # Get current stored version
            current_version = TCFAPIService.get_stored_version()

            # If we have a current version and it's newer than the incoming data, reject the save
            if current_version is not None and current_version > new_version:
                print(f"Rejecting save: Current version ({current_version}) is newer than incoming version ({new_version})")
                return False

            # Generate filenames with both versions
            new_filename = TCFAPIService.get_filename(data)
            current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
            archive_file = os.path.join(Config.ARCHIVE_DATA_DIR, new_filename)
            version_file = os.path.join(Config.CURRENT_DATA_DIR, 'version.txt')

            # Ensure directories exist
            os.makedirs(Config.CURRENT_DATA_DIR, exist_ok=True)
            os.makedirs(Config.ARCHIVE_DATA_DIR, exist_ok=True)

            # If versions are the same and file exists, no need to save
            if current_version == new_version and os.path.exists(archive_file):
                print(f"Version {new_version} already exists, skipping")
                return False

            # Archive the current version before overwriting if it exists
            if os.path.exists(current_file) and current_version:
                with open(current_file, 'r') as f:
                    current_data = json.load(f)
                    current_archive_file = os.path.join(Config.ARCHIVE_DATA_DIR, 
                                                      TCFAPIService.get_filename(current_data))
                    if not os.path.exists(current_archive_file):
                        with open(current_archive_file, 'w') as dst:
                            json.dump(current_data, dst, indent=2)
                        print(f"Archived current version as {os.path.basename(current_archive_file)}")
                        # Process the archived current version
                        TCFAPIService.process_vendor_list_file(current_archive_file)

            # Save new data
            try:
                # Save to archive first
                with open(archive_file, 'w') as f:
                    json.dump(data, f, indent=2)

                # Process the new archived file
                TCFAPIService.process_vendor_list_file(archive_file)

                # Save to current directory
                with open(current_file, 'w') as f:
                    json.dump(data, f, indent=2)

                # Save version number last (atomic operation)
                with open(version_file, 'w') as f:
                    f.write(str(new_version))

                print(f"Successfully saved {os.path.basename(archive_file)}")
                return True

            except Exception as e:
                print(f"Error saving vendor list: {e}")
                # If there was an error, try to restore the previous version
                if current_version:
                    try:
                        with open(version_file, 'w') as f:
                            f.write(str(current_version))
                    except Exception as restore_error:
                        print(f"Error restoring version number: {restore_error}")
                return False

        except Exception as e:
            print(f"Error processing vendor list: {e}")
            return False

    @staticmethod
    def check_and_update():
        """Check for new version and update if available"""
        current_version = TCFAPIService.get_current_version()
        if not current_version:
            print("Could not get current version from API")
            return False

        try:
            current_version = int(current_version)
        except (ValueError, TypeError):
            print(f"Invalid version number from API: {current_version}")
            return False

        stored_version = TCFAPIService.get_stored_version()
        
        # If we have no stored version, or the API version is newer
        if stored_version is None or current_version > stored_version:
            print(f"New version available: {current_version} (current: {stored_version})")
            data = TCFAPIService.fetch_vendor_list()
            if data:
                return TCFAPIService.save_vendor_list(data)
        else:
            print(f"Already have latest version {stored_version}")
        
        return False

    @staticmethod
    def create_subset(vendor_ids=None, purposes=None):
        """Create a subset of the vendor list based on specific criteria"""
        current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
        if not os.path.exists(current_file):
            return None

        with open(current_file, 'r') as f:
            data = json.load(f)

        subset = data.copy()
        
        if vendor_ids:
            subset['vendors'] = {
                vid: info for vid, info in data['vendors'].items()
                if vid in vendor_ids
            }
            
        if purposes:
            subset['purposes'] = {
                pid: info for pid, info in data['purposes'].items()
                if pid in purposes
            }

        return subset 