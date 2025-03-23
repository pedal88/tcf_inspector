import json
import os
from pathlib import Path

def transform_vendor(vendor_data):
    """Transform a single vendor's data according to the specified rules."""
    
    # Initialize all fields with 0 (no legal basis)
    transformed = {
        "vendor_id": vendor_data["id"],
        "vendor_name": vendor_data["name"]
    }
    
    # Initialize all purpose fields with 0
    for p in range(1, 11):  # P1-P10
        transformed[f"P{p}"] = 0
    for sp in range(1, 3):  # SP1-SP2
        transformed[f"SP{sp}"] = 0
    for f in range(1, 4):   # F1-F3
        transformed[f"F{f}"] = 0
    for sf in range(1, 3):  # SF1-SF2
        transformed[f"SF{sf}"] = 0
    
    # Process regular purposes (P1-P10)
    purposes = vendor_data.get("purposes", [])
    legIntPurposes = vendor_data.get("legIntPurposes", [])
    flexiblePurposes = vendor_data.get("flexiblePurposes", [])
    
    for p in range(1, 11):
        if p in purposes:
            if p in flexiblePurposes:
                transformed[f"P{p}"] = 3  # Both Consent and LI
            else:
                transformed[f"P{p}"] = 1  # Consent only
        elif p in legIntPurposes:
            transformed[f"P{p}"] = 2  # LI only
        elif p in flexiblePurposes:
            transformed[f"P{p}"] = 3  # Both Consent and LI
    
    # Process special purposes (always LI = 2)
    specialPurposes = vendor_data.get("specialPurposes", [])
    for sp in specialPurposes:
        if sp in [1, 2]:
            transformed[f"SP{sp}"] = 2
    
    # Process features (always LI = 2)
    features = vendor_data.get("features", [])
    for f in features:
        if f in [1, 2, 3]:
            transformed[f"F{f}"] = 2
    
    # Process special features (always Consent = 1)
    specialFeatures = vendor_data.get("specialFeatures", [])
    for sf in specialFeatures:
        if sf in [1, 2]:
            transformed[f"SF{sf}"] = 1
    
    return transformed

def process_gvl_file(input_path, output_path):
    """Process a single GVL JSON file and save the transformed data."""
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    vendors = data.get("vendors", {})
    transformed_vendors = []
    
    for vendor_id, vendor_data in vendors.items():
        transformed_vendor = transform_vendor(vendor_data)
        transformed_vendors.append(transformed_vendor)
    
    # Sort vendors by ID to maintain consistent order
    transformed_vendors.sort(key=lambda x: x["vendor_id"])
    
    # Save transformed data
    with open(output_path, 'w') as f:
        json.dump(transformed_vendors, f, indent=2)

def process_archive():
    """Process all files in the archive directory."""
    archive_dir = Path("data/archive")
    processed_dir = Path("data/archive_processed")
    
    # Create processed directory if it doesn't exist
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all JSON files in the archive directory
    for file_path in archive_dir.glob("*.json"):
        output_path = processed_dir / file_path.name
        print(f"Processing archive file {file_path.name}...")
        process_gvl_file(file_path, output_path)
        print(f"Saved processed file to {output_path}")

def process_current_file(file_path):
    """Process a single file from the current directory."""
    processed_dir = Path("data/archive_processed")
    
    # Create processed directory if it doesn't exist
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Create output path with same filename in processed directory
    output_path = processed_dir / file_path.name
    
    print(f"Processing current file {file_path.name}...")
    process_gvl_file(file_path, output_path)
    print(f"Saved processed file to {output_path}")

def main():
    """Main function that can be called to process either archive or current files."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--current":
        # Process files in current directory
        current_dir = Path("data/current")
        for file_path in current_dir.glob("*.json"):
            process_current_file(file_path)
    else:
        # Process archive directory
        process_archive()

if __name__ == "__main__":
    main() 