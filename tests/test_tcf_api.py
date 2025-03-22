import unittest
import json
import os
from app import create_app, db
from app.services.tcf_api import TCFAPIService
from app.models.vendor import Vendor
from app.models.archive import VendorArchive

class TestTCFAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_fetch_vendor_list(self):
        """Test fetching vendor list from API"""
        data = TCFAPIService.fetch_vendor_list()
        self.assertIsNotNone(data)
        self.assertIn('vendors', data)
        self.assertIn('purposes', data)

    def test_create_subset(self):
        """Test creating subset of vendor data"""
        # Mock vendor data
        test_data = {
            'vendors': {
                '1': {'name': 'Vendor 1', 'purposes': [1, 2]},
                '2': {'name': 'Vendor 2', 'purposes': [2, 3]}
            },
            'purposes': {
                '1': {'name': 'Purpose 1'},
                '2': {'name': 'Purpose 2'},
                '3': {'name': 'Purpose 3'}
            }
        }
        
        # Save test data
        current_file = os.path.join(self.app.config['CURRENT_DATA_DIR'], 'current_vendor_list.json')
        os.makedirs(os.path.dirname(current_file), exist_ok=True)
        with open(current_file, 'w') as f:
            json.dump(test_data, f)

        # Test subset creation
        subset = TCFAPIService.create_subset(vendor_ids=['1'])
        self.assertIsNotNone(subset)
        self.assertEqual(len(subset['vendors']), 1)
        self.assertIn('1', subset['vendors'])
        self.assertNotIn('2', subset['vendors'])

if __name__ == '__main__':
    unittest.main() 