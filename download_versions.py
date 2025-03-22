from app.services.tcf_api import TCFAPIService
import time
import requests

def download_range(start_version, end_version):
    """Download vendor list versions from start_version to end_version inclusive"""
    print(f'Starting download of versions from {start_version} to {end_version}')
    
    for version in range(start_version, end_version + 1):
        print(f'\nFetching version {version}...')
        data = TCFAPIService.fetch_vendor_list(version=version)
        if data:
            TCFAPIService.save_to_archive_only(data)
            # Add small delay between requests to be nice to the server
            time.sleep(0.5)
        else:
            print(f'Failed to fetch version {version}')

def test_endpoint(version):
    """Test if a GVL version endpoint exists"""
    base_url = f"https://vendor-list.consensu.org/v{version}"
    test_url = f"{base_url}/vendor-list.json"
    try:
        response = requests.get(test_url)
        response.raise_for_status()
        data = response.json()
        print(f"\nGVL v{version} endpoint exists!")
        print(f"Sample data: gvlSpecificationVersion={data.get('gvlSpecificationVersion')}, tcfPolicyVersion={data.get('tcfPolicyVersion')}")
        return True
    except Exception as e:
        print(f"\nGVL v{version} endpoint not accessible: {str(e)}")
        return False

def test_v1_endpoints():
    """Test different possible v1 archive endpoints"""
    endpoints = [
        "https://vendor-list.consensu.org/v1/archives/vendor-list-v1.json",
        "https://vendor-list.consensu.org/archives/v1/vendor-list.json",
        "https://vendor-list.consensu.org/v1/vendorlist.json",
        "https://vendor-list.consensu.org/archives/vendorlist-v1.json"
    ]
    
    for url in endpoints:
        print(f"\nTesting endpoint: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            print("Success! Found data:")
            print(f"gvlSpecificationVersion={data.get('gvlSpecificationVersion')}")
            print(f"tcfPolicyVersion={data.get('tcfPolicyVersion')}")
            print(f"vendorListVersion={data.get('vendorListVersion')}")
            return url
        except Exception as e:
            print(f"Failed: {str(e)}")
    
    return None

if __name__ == '__main__':
    print("Testing possible v1 endpoints...")
    working_endpoint = test_v1_endpoints()
    if working_endpoint:
        download_range(2, 97) 