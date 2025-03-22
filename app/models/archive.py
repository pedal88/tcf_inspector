from app import db
from datetime import datetime

class VendorArchive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String(50), nullable=False)
    snapshot_data = db.Column(db.JSON, nullable=False)
    snapshot_date = db.Column(db.DateTime, default=datetime.utcnow)
    changes = db.Column(db.JSON)  # Store what changed from previous version

    def __repr__(self):
        return f'<VendorArchive {self.vendor_id} {self.snapshot_date}>'

    @staticmethod
    def create_snapshot(vendor_id, data, changes=None):
        """Create an archive snapshot of vendor data"""
        archive = VendorArchive(
            vendor_id=str(vendor_id),
            snapshot_data=data,
            changes=changes
        )
        return archive 