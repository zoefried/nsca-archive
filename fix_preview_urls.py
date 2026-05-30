#!/usr/bin/env python3
"""
Fix preview URLs in nsca_catalog.json by removing &dl=0 from all previewUrl fields.
Run from the same folder as nsca_catalog.json.
"""

import json

CATALOG_FILE = 'nsca_catalog.json'

with open(CATALOG_FILE, 'r') as f:
    catalog = json.load(f)

fixed = 0
for record in catalog:
    url = record.get('previewUrl', '')
    if url and '&dl=0' in url:
        record['previewUrl'] = url.replace('&dl=0', '')
        fixed += 1

with open(CATALOG_FILE, 'w') as f:
    json.dump(catalog, f, indent=2)

print(f"Fixed {fixed} URLs. Upload nsca_catalog.json to GitHub.")
