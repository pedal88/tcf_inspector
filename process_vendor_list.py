import json
import os
from datetime import datetime

def process_vendor_list(input_file, output_file):
    # Read the input file
    with open(input_file, 'r') as f:
        data = json.load(f)

    processed_vendors = []
    
    # Process each vendor
    vendors = data.get('vendors', {})
    for vendor_id, vendor in vendors.items():
        processed_vendor = {
            'vendor_id': vendor.get('id'),
            'vendor_name': vendor.get('name', ''),
        }
        
        # Process Purposes (P1-P10)
        purposes = vendor.get('purposes', [])
        legIntPurposes = vendor.get('legIntPurposes', [])
        for i in range(1, 11):
            processed_vendor[f'P{i}'] = [
                1 if i in purposes else 0,
                1 if i in legIntPurposes else 0
            ]
        
        # Process Special Purposes (SP1-SP2)
        specialPurposes = vendor.get('specialPurposes', [])
        for i in range(1, 3):
            processed_vendor[f'SP{i}'] = [
                0,  # Special Purposes don't use consent
                1 if i in specialPurposes else 0
            ]
        
        # Process Features (F1-F3)
        features = vendor.get('features', [])
        for i in range(1, 4):
            processed_vendor[f'F{i}'] = [
                0,  # Features don't use consent/legitimate interest
                1 if i in features else 0
            ]
        
        # Process Special Features (SF1-SF2)
        specialFeatures = vendor.get('specialFeatures', [])
        for i in range(1, 3):
            processed_vendor[f'SF{i}'] = [
                1 if i in specialFeatures else 0,
                0  # Special Features don't use legitimate interest
            ]
        
        processed_vendors.append(processed_vendor)
    
    # Sort vendors by ID
    processed_vendors.sort(key=lambda x: x['vendor_id'])
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the processed data to output file
    with open(output_file, 'w') as f:
        json.dump(processed_vendors, f, indent=2)

def process_all_files():
    archive_dir = 'data/archive'
    processed_dir = 'data/archive_processed'
    
    # Create processed directory if it doesn't exist
    os.makedirs(processed_dir, exist_ok=True)
    
    # Get all JSON files from archive directory
    json_files = [f for f in os.listdir(archive_dir) if f.endswith('.json')]
    
    # Process each file
    for json_file in json_files:
        input_path = os.path.join(archive_dir, json_file)
        output_path = os.path.join(processed_dir, json_file.replace('vendor_list_gvl', 'vendor_list_processed'))
        
        try:
            process_vendor_list(input_path, output_path)
            print(f"Processed {json_file} -> {os.path.basename(output_path)}")
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")

if __name__ == '__main__':
    process_all_files()
    print("Processing complete.") 