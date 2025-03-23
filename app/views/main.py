from flask import Blueprint, jsonify, render_template, request
from app.services.tcf_api import TCFAPIService
import os
import json
from app.config import Config
from datetime import datetime

main_bp = Blueprint('main', __name__)

def get_available_vendor_files():
    """Get list of all vendor list files from archive_processed directory."""
    files = []
    
    # Add files from archive_processed
    archive_files = [f for f in os.listdir(Config.ARCHIVE_PROCESSED_DIR) 
                    if f.endswith('.json')]
    
    # Create a list of tuples with (display_name, filename)
    file_info = []
    for filename in archive_files:
        display_name = filename.split('_')[0]  # Get just the date part
        file_info.append({'display': display_name, 'filename': filename})
    
    # Sort by filename in reverse order (most recent first)
    file_info.sort(key=lambda x: x['filename'], reverse=True)
    
    return file_info

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/vendor/table')
def vendor_table():
    # Get list of available files
    available_files = get_available_vendor_files()
    
    if not available_files:
        return render_template('vendor_table.html', 
                             error="No processed vendor data files found",
                             available_files=[],
                             selected_file=None)
    
    # Get selected file from query parameters or use the most recent one
    selected_file = request.args.get('file')
    if not selected_file or not any(f['filename'] == selected_file for f in available_files):
        selected_file = available_files[0]['filename']  # Most recent file
    
    processed_file_path = os.path.join(Config.ARCHIVE_PROCESSED_DIR, selected_file)
    
    # Find the corresponding original file in archive
    # Convert filename from processed format to original format
    # From: YYYY-MM-DD_vendor_list_processed_vXX.json
    # To:   YYYY-MM-DD_vendor_list_gvl3_tcf5_vXX.json
    date_part = selected_file.split('_')[0]  # Get YYYY-MM-DD
    version_part = selected_file.split('_')[-1]  # Get vXX.json
    original_file = f"{date_part}_vendor_list_gvl3_tcf5_{version_part}"
    original_file_path = os.path.join(Config.ARCHIVE_DATA_DIR, original_file)
    
    metadata_path = os.path.join(Config.VENDOR_METADATA_DIR, 'vendor_metadata.json')
    
    # Load and parse the files
    try:
        # Load processed vendor data
        with open(processed_file_path, 'r') as f:
            vendors = json.load(f)
            
        # Load metadata from original GVL file
        gvl_metadata = {
            'gvlSpecificationVersion': 'N/A',
            'vendorListVersion': 'N/A',
            'tcfPolicyVersion': 'N/A',
            'lastUpdated': 'N/A'
        }
        
        if os.path.exists(original_file_path):
            print(f"Loading metadata from original file: {original_file_path}")
            with open(original_file_path, 'r') as f:
                original_data = json.load(f)
                gvl_metadata = {
                    'gvlSpecificationVersion': original_data.get('gvlSpecificationVersion', 'N/A'),
                    'vendorListVersion': original_data.get('vendorListVersion', 'N/A'),
                    'tcfPolicyVersion': original_data.get('tcfPolicyVersion', 'N/A'),
                    'lastUpdated': original_data.get('lastUpdated', 'N/A')
                }
                print("Loaded GVL Metadata:", gvl_metadata)
        else:
            print(f"Original GVL file not found: {original_file_path}")
            # Try to find any matching file by date
            archive_files = [f for f in os.listdir(Config.ARCHIVE_DATA_DIR) if f.startswith(date_part) and f.endswith(version_part)]
            if archive_files:
                original_file_path = os.path.join(Config.ARCHIVE_DATA_DIR, archive_files[0])
                print(f"Found alternative file: {original_file_path}")
                with open(original_file_path, 'r') as f:
                    original_data = json.load(f)
                    gvl_metadata = {
                        'gvlSpecificationVersion': original_data.get('gvlSpecificationVersion', 'N/A'),
                        'vendorListVersion': original_data.get('vendorListVersion', 'N/A'),
                        'tcfPolicyVersion': original_data.get('tcfPolicyVersion', 'N/A'),
                        'lastUpdated': original_data.get('lastUpdated', 'N/A')
                    }
                    print("Loaded GVL Metadata from alternative file:", gvl_metadata)
        
        # Load vendor metadata if it exists
        vendor_metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                vendor_metadata = json.load(f)
        
        # Merge metadata with vendor data
        for vendor in vendors:
            vendor_id = str(vendor['vendor_id'])
            if vendor_id in vendor_metadata:
                metadata = vendor_metadata[vendor_id]
                vendor['vendor_status'] = metadata.get('vendor_status', 'no')  # Default to 'no' if not set
                vendor['vendor_types'] = metadata.get('vendor_type', [])  # Changed from vendor_types to vendor_type
                vendor['mbl_audited'] = metadata.get('mbl_audited', 0)  # Default to 0 (not audited) if not set
            else:
                vendor['vendor_status'] = 'no'  # Default status for vendors without metadata
                vendor['vendor_types'] = []  # Default empty list for vendors without metadata
                vendor['mbl_audited'] = 0  # Default to not audited for vendors without metadata
        
        # Sort vendors by ID
        vendors = sorted(vendors, key=lambda x: x['vendor_id'])
        
        # Define purposes for the template
        purposes = [
            # Standard Purposes
            {'id': 'P1', 'name': 'Store and/or access information on a device'},
            {'id': 'P2', 'name': 'Select basic ads'},
            {'id': 'P3', 'name': 'Create a personalised ads profile'},
            {'id': 'P4', 'name': 'Select personalised ads'},
            {'id': 'P5', 'name': 'Create a personalised content profile'},
            {'id': 'P6', 'name': 'Select personalised content'},
            {'id': 'P7', 'name': 'Measure ad performance'},
            {'id': 'P8', 'name': 'Measure content performance'},
            {'id': 'P9', 'name': 'Apply market research to generate audience insights'},
            {'id': 'P10', 'name': 'Develop and improve products'},
            # Special Purposes
            {'id': 'SP1', 'name': 'Ensure security, prevent fraud, and debug'},
            {'id': 'SP2', 'name': 'Technically deliver ads or content'},
            # Features
            {'id': 'F1', 'name': 'Match and combine offline data sources'},
            {'id': 'F2', 'name': 'Link different devices'},
            {'id': 'F3', 'name': 'Receive and use automatically-sent device characteristics for identification'},
            # Special Features
            {'id': 'SF1', 'name': 'Use precise geolocation data'},
            {'id': 'SF2', 'name': 'Actively scan device characteristics for identification'}
        ]
        
        return render_template('vendor_table.html',
                             vendors=vendors,
                             purposes=purposes,
                             available_files=available_files,
                             selected_file=selected_file,
                             gvl_metadata=gvl_metadata)
    
    except Exception as e:
        return render_template('vendor_table.html',
                             error=f"Error loading vendor data: {str(e)}",
                             available_files=available_files,
                             selected_file=selected_file,
                             gvl_metadata={
                                 'gvlSpecificationVersion': 'N/A',
                                 'vendorListVersion': 'N/A',
                                 'tcfPolicyVersion': 'N/A',
                                 'lastUpdated': 'N/A'
                             })

@main_bp.route('/vendor/history/<vendor_id>')
def vendor_history(vendor_id):
    # Get the latest processed file from archive_processed
    archive_files = sorted([f for f in os.listdir(Config.ARCHIVE_PROCESSED_DIR) 
                          if f.endswith('.json') and 'vendor_list_processed' in f],
                         reverse=True)
    
    if not archive_files:
        return render_template('vendor_history.html', error="No vendor data available")
    
    latest_file = archive_files[0]
    file_path = os.path.join(Config.ARCHIVE_PROCESSED_DIR, latest_file)
    
    try:
        with open(file_path, 'r') as f:
            vendors_data = json.load(f)
            
        # Create a lookup dictionary for vendors
        vendors = {str(v['vendor_id']): v for v in vendors_data}
        
        # Get all vendors for selection
        all_vendors = [{'id': str(v['vendor_id']), 'name': v['vendor_name']} for v in vendors_data]
        all_vendors.sort(key=lambda x: x['name'])
        
        # If 'latest' is specified, show vendor selection page
        if vendor_id == 'latest':
            return render_template('vendor_history.html', 
                                vendors=all_vendors,
                                show_selection=True)
        
        # Convert vendor_id to string to match JSON format
        vendor_id = str(vendor_id)
        
        # Get specific vendor data
        vendor = vendors.get(vendor_id)
        if not vendor:
            return render_template('vendor_history.html', 
                                error=f"Vendor {vendor_id} not found",
                                vendors=all_vendors,
                                show_selection=True)
        
        # Get historical data from archive_processed
        history = []
        previous_purposes = None
        previous_data = None
        
        for archive_file in sorted(archive_files):
            try:
                with open(os.path.join(Config.ARCHIVE_PROCESSED_DIR, archive_file), 'r') as f:
                    archive_data = json.load(f)
                    # Find the vendor in the list
                    archive_vendor = next((v for v in archive_data if str(v['vendor_id']) == vendor_id), None)
                    
                    if archive_vendor:
                        # Get the date from the filename (YYYY-MM-DD)
                        date_str = archive_file.split('_')[0]
                        
                        # Get current purposes status
                        current_purposes = {}
                        for key in ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']:
                            if archive_vendor[key][0] == 1:  # Consent
                                current_purposes[key] = 'consent'
                            elif archive_vendor[key][1] == 1:  # Legitimate Interest
                                current_purposes[key] = 'legitimate_interest'
                        
                        # Calculate changes from previous version
                        changes = {
                            'added_purposes': [],
                            'removed_purposes': [],
                            'changed_purposes': []
                        }
                        
                        if previous_purposes is not None:
                            for key in current_purposes:
                                if key not in previous_purposes:
                                    changes['added_purposes'].append(key)
                                elif previous_purposes[key] != current_purposes[key]:
                                    changes['changed_purposes'].append(key)
                            
                            for key in previous_purposes:
                                if key not in current_purposes:
                                    changes['removed_purposes'].append(key)
                        
                        # Check if there are any changes
                        has_changes = (previous_purposes is None or 
                                    changes['added_purposes'] or 
                                    changes['removed_purposes'] or 
                                    changes['changed_purposes'])
                        
                        if has_changes:
                            history.append({
                                'version': archive_file,
                                'data': archive_vendor,
                                'date': date_str,
                                'purposes': current_purposes,
                                'changes': changes
                            })
                        
                        previous_purposes = current_purposes
                        previous_data = archive_vendor
                        
            except Exception as e:
                print(f"Error reading archive file {archive_file}: {str(e)}")
                continue
        
        # Sort history by date in descending order
        history.sort(key=lambda x: x['date'], reverse=True)
        
        # Define purposes for the template
        purposes = [
            # Standard Purposes
            {'id': 'P1', 'name': 'Store and/or access information on a device', 'type': 'P'},
            {'id': 'P2', 'name': 'Select basic ads', 'type': 'P'},
            {'id': 'P3', 'name': 'Create a personalised ads profile', 'type': 'P'},
            {'id': 'P4', 'name': 'Select personalised ads', 'type': 'P'},
            {'id': 'P5', 'name': 'Create a personalised content profile', 'type': 'P'},
            {'id': 'P6', 'name': 'Select personalised content', 'type': 'P'},
            {'id': 'P7', 'name': 'Measure ad performance', 'type': 'P'},
            {'id': 'P8', 'name': 'Measure content performance', 'type': 'P'},
            {'id': 'P9', 'name': 'Apply market research to generate audience insights', 'type': 'P'},
            {'id': 'P10', 'name': 'Develop and improve products', 'type': 'P'},
            # Special Purposes
            {'id': 'SP1', 'name': 'Ensure security, prevent fraud, and debug', 'type': 'SP'},
            {'id': 'SP2', 'name': 'Technically deliver ads or content', 'type': 'SP'},
            # Features
            {'id': 'F1', 'name': 'Match and combine offline data sources', 'type': 'F'},
            {'id': 'F2', 'name': 'Link different devices', 'type': 'F'},
            {'id': 'F3', 'name': 'Receive and use automatically-sent device characteristics for identification', 'type': 'F'},
            # Special Features
            {'id': 'SF1', 'name': 'Use precise geolocation data', 'type': 'SF'},
            {'id': 'SF2', 'name': 'Actively scan device characteristics for identification', 'type': 'SF'}
        ]
        
        return render_template('vendor_history.html', 
                            vendor=vendor,
                            history=history,
                            vendors=all_vendors,
                            purposes=purposes)
                            
    except Exception as e:
        return render_template('vendor_history.html',
                            error=f"Error loading vendor data: {str(e)}",
                            vendors=all_vendors,
                            show_selection=True)

@main_bp.route('/vendor/compare')
def vendor_compare():
    vendor1_id = request.args.get('vendor1')
    vendor2_id = request.args.get('vendor2')
    
    # Get the latest processed file from archive_processed
    archive_files = sorted([f for f in os.listdir(Config.ARCHIVE_PROCESSED_DIR) 
                          if f.endswith('.json') and 'vendor_list_processed' in f],
                         reverse=True)
    
    if not archive_files:
        return render_template('vendor_compare.html', error="No vendor data available")
    
    latest_file = archive_files[0]
    file_path = os.path.join(Config.ARCHIVE_PROCESSED_DIR, latest_file)
    
    try:
        with open(file_path, 'r') as f:
            vendors_data = json.load(f)
        
        # Create a lookup dictionary for vendors
        vendors = {str(v['vendor_id']): v for v in vendors_data}
        
        # Get all vendors for the dropdown lists
        all_vendors = [{'id': str(v['vendor_id']), 'name': v['vendor_name']} 
                      for v in vendors_data]
        all_vendors.sort(key=lambda x: x['name'])
        
        # If vendors are selected, get their data
        if vendor1_id and vendor2_id:
            vendor1 = vendors.get(vendor1_id)
            vendor2 = vendors.get(vendor2_id)
            
            if not vendor1 or not vendor2:
                return render_template('vendor_compare.html',
                                    error="One or both vendors not found",
                                    vendors=all_vendors)
            
            # Define purposes for comparison
            purposes = [
                {'id': 'P1', 'name': 'Store and/or access information on a device', 'type': 'P'},
                {'id': 'P2', 'name': 'Select basic ads', 'type': 'P'},
                {'id': 'P3', 'name': 'Create a personalised ads profile', 'type': 'P'},
                {'id': 'P4', 'name': 'Select personalised ads', 'type': 'P'},
                {'id': 'P5', 'name': 'Create a personalised content profile', 'type': 'P'},
                {'id': 'P6', 'name': 'Select personalised content', 'type': 'P'},
                {'id': 'P7', 'name': 'Measure ad performance', 'type': 'P'},
                {'id': 'P8', 'name': 'Measure content performance', 'type': 'P'},
                {'id': 'P9', 'name': 'Apply market research to generate audience insights', 'type': 'P'},
                {'id': 'P10', 'name': 'Develop and improve products', 'type': 'P'},
                {'id': 'SP1', 'name': 'Ensure security, prevent fraud, and debug', 'type': 'SP'},
                {'id': 'SP2', 'name': 'Technically deliver ads or content', 'type': 'SP'},
                {'id': 'F1', 'name': 'Match and combine offline data sources', 'type': 'F'},
                {'id': 'F2', 'name': 'Link different devices', 'type': 'F'},
                {'id': 'F3', 'name': 'Receive and use automatically-sent device characteristics for identification', 'type': 'F'},
                {'id': 'SF1', 'name': 'Use precise geolocation data', 'type': 'SF'},
                {'id': 'SF2', 'name': 'Actively scan device characteristics for identification', 'type': 'SF'}
            ]
            
            return render_template('vendor_compare.html',
                                vendors=all_vendors,
                                vendor1=vendor1,
                                vendor2=vendor2,
                                purposes=purposes)
    
    except Exception as e:
        return render_template('vendor_compare.html',
                            error=f"Error loading vendor data: {str(e)}",
                            vendors=all_vendors)
    
    return render_template('vendor_compare.html', vendors=all_vendors) 