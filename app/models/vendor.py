from app import db
from datetime import datetime

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    purposes = db.Column(db.JSON)
    features = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Vendor {self.name}>'

    @staticmethod
    def from_json(data):
        """Create a Vendor instance from JSON data"""
        vendor = Vendor(
            vendor_id=str(data.get('id')),
            name=data.get('name'),
            purposes=data.get('purposes'),
            features=data.get('features')
        )
        return vendor 