from flask import Blueprint, jsonify, render_template, request
from app.services.tcf_api import TCFAPIService
import os
import json
from app.config import Config
from datetime import datetime

main_bp = Blueprint('main', __name__)

def get_available_vendor_files():
    """Get list of all vendor list files from archive and current directories."""
    files = []
    
    # Add files from archive
    archive_files = [f for f in os.listdir(Config.ARCHIVE_DATA_DIR) 
                    if f.endswith('.json') and 'vendor_list' in f]
    files.extend(sorted(archive_files))
    
    # Add current file if it exists
    current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
    if os.path.exists(current_file):
        files.append('current_vendor_list.json')
    
    return files

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/vendor/table')
def vendor_table():
    # Get list of available files
    available_files = get_available_vendor_files()
    
    # Get selected file from query parameters
    selected_file = request.args.get('file')
    
    # If no file is selected or the file doesn't exist, use the current file
    if not selected_file or selected_file not in available_files:
        selected_file = 'current_vendor_list.json'
    
    # Determine the file path based on selection
    if selected_file == 'current_vendor_list.json':
        file_path = os.path.join(Config.CURRENT_DATA_DIR, selected_file)
    else:
        file_path = os.path.join(Config.ARCHIVE_DATA_DIR, selected_file)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return render_template('vendor_table.html', 
                             error="Selected vendor data file not found",
                             available_files=available_files,
                             selected_file=selected_file)
    
    # Load and parse the file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract vendors and purposes for the template
        vendors = [{'id': k, **v} for k, v in data.get('vendors', {}).items()]
        purposes = [{'id': k, **v} for k, v in data.get('purposes', {}).items()]
        
        return render_template('vendor_table.html',
                             vendors=vendors,
                             purposes=purposes,
                             available_files=available_files,
                             selected_file=selected_file)
    
    except Exception as e:
        return render_template('vendor_table.html',
                             error=f"Error loading vendor data: {str(e)}",
                             available_files=available_files,
                             selected_file=selected_file)

@main_bp.route('/vendor/history/<vendor_id>')
def vendor_history(vendor_id):
    current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
    if not os.path.exists(current_file):
        return render_template('vendor_history.html', error="No vendor data available")
        
    with open(current_file, 'r') as f:
        data = json.load(f)
    
    # Get all vendors for selection
    all_vendors = [{'id': k, 'name': v.get('name')} for k, v in data.get('vendors', {}).items()]
    all_vendors.sort(key=lambda x: x['name'])  # Sort vendors by name
    
    # If 'latest' is specified, show vendor selection page
    if vendor_id == 'latest':
        return render_template('vendor_history.html', 
                             vendors=all_vendors,
                             show_selection=True)
    
    # Convert vendor_id to string to match JSON format
    vendor_id = str(vendor_id)
    
    # Get specific vendor data
    vendor = data.get('vendors', {}).get(vendor_id)
    if not vendor:
        return render_template('vendor_history.html', 
                             error=f"Vendor {vendor_id} not found",
                             vendors=all_vendors,
                             show_selection=True)
    
    # Convert current vendor purposes to strings
    vendor['purposes'] = [str(p) for p in vendor.get('purposes', [])]
    
    # Get historical data from archive
    history = []
    archive_files = sorted([f for f in os.listdir(Config.ARCHIVE_DATA_DIR) 
                          if f.endswith('.json') and 'vendor_list' in f])
    
    previous_purposes = None
    previous_data = None
    for archive_file in archive_files:
        try:
            with open(os.path.join(Config.ARCHIVE_DATA_DIR, archive_file), 'r') as f:
                archive_data = json.load(f)
                archive_vendor = archive_data.get('vendors', {}).get(vendor_id)
                if archive_vendor:
                    # Format the date nicely
                    last_updated = archive_data.get('lastUpdated', '')
                    try:
                        date_obj = datetime.fromtimestamp(int(last_updated) / 1000)
                        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        formatted_date = last_updated
                    
                    # Get current purposes
                    current_purposes = set(str(p) for p in archive_vendor.get('purposes', []))
                    
                    # Calculate changes from previous version
                    changes = {
                        'added_purposes': list(current_purposes - previous_purposes) if previous_purposes is not None else [],
                        'removed_purposes': list(previous_purposes - current_purposes) if previous_purposes is not None else [],
                    }
                    
                    # Check if there are any changes
                    has_changes = (previous_purposes is None or 
                                 current_purposes != previous_purposes)
                    
                    if has_changes:
                        history.append({
                            'version': archive_file,
                            'data': archive_vendor,
                            'date': formatted_date,
                            'purposes': current_purposes,
                            'changes': changes
                        })
                    
                    previous_purposes = current_purposes
                    previous_data = archive_vendor
                    
                    # Store purposes data for the template
                    if not hasattr(vendor_history, 'purposes'):
                        vendor_history.purposes = [
                            {'id': k, 'name': v.get('name')} 
                            for k, v in archive_data.get('purposes', {}).items()
                        ]
                        vendor_history.purposes.sort(key=lambda x: int(x['id']))
                    
        except Exception as e:
            print(f"Error reading archive file {archive_file}: {str(e)}")
            continue
    
    # Sort history by date in descending order
    history.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('vendor_history.html', 
                         vendor=vendor,
                         history=history,
                         vendors=all_vendors,
                         purposes=getattr(vendor_history, 'purposes', []))

@main_bp.route('/vendor/compare')
def vendor_compare():
    vendor1_id = request.args.get('vendor1')
    vendor2_id = request.args.get('vendor2')
    
    current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
    if not os.path.exists(current_file):
        return render_template('vendor_compare.html', error="No vendor data available")
        
    with open(current_file, 'r') as f:
        data = json.load(f)
    
    # Get all vendors for the dropdown lists
    vendors = [{'id': k, 'name': v.get('name')} for k, v in data.get('vendors', {}).items()]
    
    # If vendors are selected, get their data
    if vendor1_id and vendor2_id:
        subset = TCFAPIService.create_subset(vendor_ids=[vendor1_id, vendor2_id])
        if not subset:
            return render_template('vendor_compare.html', 
                                error="Could not create comparison",
                                vendors=vendors)
        
        vendor1 = subset['vendors'].get(vendor1_id)
        vendor2 = subset['vendors'].get(vendor2_id)
        purposes = [{'id': k, **v} for k, v in subset.get('purposes', {}).items()]
        
        return render_template('vendor_compare.html',
                             vendors=vendors,
                             vendor1=vendor1,
                             vendor2=vendor2,
                             purposes=purposes)
    
    return render_template('vendor_compare.html', vendors=vendors) 