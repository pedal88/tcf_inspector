from flask import Blueprint, jsonify, render_template, request
from app.services.tcf_api import TCFAPIService
import os
import json
from app.config import Config

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/vendor/table')
def vendor_table():
    current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
    if not os.path.exists(current_file):
        return render_template('vendor_table.html', error="No vendor data available")
        
    with open(current_file, 'r') as f:
        data = json.load(f)
    
    # Extract vendors and purposes for the template
    vendors = [{'id': k, **v} for k, v in data.get('vendors', {}).items()]
    purposes = [{'id': k, **v} for k, v in data.get('purposes', {}).items()]
    
    return render_template('vendor_table.html', vendors=vendors, purposes=purposes)

@main_bp.route('/vendor/history/<vendor_id>')
def vendor_history(vendor_id):
    current_file = os.path.join(Config.CURRENT_DATA_DIR, 'current_vendor_list.json')
    if not os.path.exists(current_file):
        return render_template('vendor_history.html', error="No vendor data available")
        
    with open(current_file, 'r') as f:
        data = json.load(f)
    
    vendor = data.get('vendors', {}).get(vendor_id)
    if not vendor:
        return render_template('vendor_history.html', error="Vendor not found")
    
    # Get historical data
    history = []  # This will be populated from the archive
    
    return render_template('vendor_history.html', vendor=vendor, history=history)

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