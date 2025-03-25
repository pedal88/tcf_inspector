# TCF Inspector

A Python tool for downloading and inspecting IAB Europe's Transparency and Consent Framework (TCF) vendor lists.

## Features

- Download vendor lists from IAB Europe's TCF endpoints
- Support for TCF v2 and v3 formats
- Automatic archiving of vendor lists
- Version tracking and management

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To download vendor lists:
```python
python download_versions.py
```

## Project Structure

- `app/` - Main application code
  - `services/` - Service layer including TCF API client
- `data/` - Data storage
  - `archive/` - Archived vendor lists

## License

MIT License 

## Links
https://iabtcf.com/api/core/classes/gvl.html