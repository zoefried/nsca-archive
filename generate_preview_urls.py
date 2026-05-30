#!/usr/bin/env python3
"""
NSCA Archive — Dropbox Preview URL Generator
Reads nsca_catalog.json, generates a shared link for each PDF,
writes the URLs back into the JSON as a 'previewUrl' field.

Usage:
  1. Paste your Dropbox access token below (between the quotes)
  2. Make sure nsca_catalog.json is in the same folder as this script
  3. Run: python3 generate_preview_urls.py
  4. Upload the updated nsca_catalog.json to GitHub
"""

import json
import time
import urllib.request
import urllib.error

# ── PASTE YOUR TOKEN HERE ────────────────────────────────────────────────────
ACCESS_TOKEN = 'sl.u.AGhds5W7KNT6Laxfl03Cw5ss20pqdgPDXkP4IVAj5dcZb0kvDc8rSqwgnQbCYTGIGNiOTou7OCCBfjwjpA47qjXy-3b-4rLtyrzl1gE1Dr1i8yK_ZaSrxDdh5jggHQYWp74M-4dg0mhM8jUuI7DHOyCkdEKC9WlItwTioa5gWfg6l9uIp28SYuI2XumFTlYR2QWpEnstysm62yjW9X6GklpIuE67wnxAz75g8F4Z2UqobaEo5u7UwbaRu7Xq6hMiCf62Pl467vzzZPsncwEMywewAka_sJBnrPEj_rqoa5wmEBiN-LxKpqgvwEz_RpfBlBdS37UG-ykdPtYFqTKxI_tEU9jqU6UIwOoCap2DTEhUabCLSyIQUIdK-X6wyhTfD0K6MOlpGdRv00X7Yv_Hc9yELnRVmPrvVdc-JzJnMAAfHKXzIvReNe84WGyJ8t1GQK2fkzSUAG61yW0VR52hv0iiPlJwc7cn22dj38YbSdGHYPlJIx5mqXSMG5J6eYsvDBGKw85N4_eMyzdyWEmp-5NhkXEDXY56Hw6xzoT1HIA70_SXjvUwafhPakcf8DZDJxXCfSV0wPurdzzRiofZzc2KgMEjjBIxEwn4rdP4gct85IFdbynoyCyZ3yGj7D2vrkC8t2eS9GRIIaz6iKZNk86ZAtwu6mNrEkPOqXiiFz36uIMU4RWq5nKz-dGcT4GcguwFF1jIkBUKO47ghcQOMJ9WlST4Qo0jatbodOCGQPBMr0eaVaij5FzUGqwgGTiV80Gnm1muy7GOsvHhCgxg3HWKcspZOC0KUnqvPtIxnRVLvLLDqHChTrXBLfUDT9gnQfy3euqskJrFMcg65T6a_bjXA7MWfNN6SCbpL3DBvTVUG1b-7t1OAPPXCgBsYuI6pmkznu_EP9SIJrmsGyTAcdu0TR_gSVXhCVnm-CcQ1EbovdEq_6SQbl3FvVW0IwK39X51ctRWf9VlMYfTkyVJFrZnDPBWZWBim35xDG7ifJNUiVf2khAW_6teC1MfQybwhVQtrDjsT0LpDVvHPu36kz3oyBaA1zuP1GYBknszSljqTArpjgVT8g9KhORfX_wxz4zTu4QhvKEF7DlObGUdI1a17TfkMgiBo8Zq-sxuE8-gMfgIxU_9yHFXot9ULhHzRn3HNo13U5__xAi42ZjUkYHavFzZZzGscRcUHytFDZTBFh1IYq0kAhrkhn0lL_tJDKOIELqEw8qcXfUA8PdUL2rHyLZp60Yh3sK8WazErVJxzHPiUjBTFz1PrQxvCLnm4d_ECUizkmW8BXvEd-5BSXX_A3PwEdojVgsAsOWsqHqTfUtqQbADSK0KazeEjfNPfiyXc9lI3IcfL1Z8TOFYp6H5RINi6CoCZInkF-5WaPWLMD0tZPYIsnKr_IZXN4qpEixBD07OJQ3FCngHQdr0L1d_bhZeL7vRiUVPWVNxR917Ot6ZZsPNOhHRLO1d9mF4gBwLYuwDx8b35zN6D7QrhKJJ'
# ────────────────────────────────────────────────────────────────────────────

CATALOG_FILE = 'nsca_catalog.json'
DROPBOX_FOLDER = '/Historical -NS'  # Leading slash, matches Dropbox path


def get_or_create_shared_link(path):
    """Return a direct-download shared link for the given Dropbox path."""
    dropbox_path = f"{DROPBOX_FOLDER}/{path.split('/')[-1]}"

    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

    # First, try to get an existing shared link
    data = json.dumps({'path': dropbox_path}).encode()
    req = urllib.request.Request(
        'https://api.dropboxapi.com/2/sharing/list_shared_links',
        data=data, headers=headers
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            links = result.get('links', [])
            if links:
                url = links[0]['url']
                # Convert to direct download link
                return url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '')
    except urllib.error.HTTPError:
        pass

    # No existing link — create one
    data = json.dumps({
        'path': dropbox_path,
        'settings': {'requested_visibility': 'public'}
    }).encode()
    req = urllib.request.Request(
        'https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings',
        data=data, headers=headers
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            url = result['url']
            return url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '')
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Error: {body}")
        return None


def main():
    if ACCESS_TOKEN == 'PASTE_YOUR_TOKEN_HERE':
        print("ERROR: You need to paste your Dropbox access token into the script first.")
        return

    with open(CATALOG_FILE, 'r') as f:
        catalog = json.load(f)

    total   = len(catalog)
    updated = 0
    skipped = 0

    for i, record in enumerate(catalog):
        filename = record['path'].split('/')[-1]
        print(f"[{i+1}/{total}] {filename}", end=' ... ', flush=True)

        # Skip if already has a preview URL
        if record.get('previewUrl'):
            print("already has URL, skipping")
            skipped += 1
            continue

        url = get_or_create_shared_link(record['path'])
        if url:
            record['previewUrl'] = url
            print(f"✓")
            updated += 1
        else:
            print("✗ failed")

        # Be polite to the API
        time.sleep(0.3)

    with open(CATALOG_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)

    print(f"\nDone. {updated} URLs added, {skipped} skipped. Saved to {CATALOG_FILE}.")
    print("Next: upload nsca_catalog.json to GitHub.")


if __name__ == '__main__':
    main()
