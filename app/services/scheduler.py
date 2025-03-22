from app import scheduler
from app.services.tcf_api import TCFAPIService
from app.config import Config

def update_vendor_data():
    """Check for and download new vendor data if available"""
    print("Checking for vendor list updates...")
    if TCFAPIService.check_and_update():
        print("Updated to new version")
    else:
        print("No update needed or update failed")

def schedule_data_updates():
    """Schedule periodic updates of vendor data"""
    scheduler.add_job(
        func=update_vendor_data,
        trigger='interval',
        minutes=Config.UPDATE_INTERVAL.total_seconds() / 60,
        id='update_vendor_data',
        replace_existing=True
    )
    
    # Run initial update
    update_vendor_data() 