#!/usr/bin/env python3
"""
NSCA Archive — PDF Thumbnail Generator
Converts the first page of each PDF in Historical -NS to a JPG thumbnail,
saves them to a 'thumbnails' folder, and updates previewUrl in nsca_catalog.json
to point to the thumbnail on GitHub Pages.

Requirements:
  brew install poppler

Usage:
  1. Set GITHUB_PAGES_URL below to your GitHub Pages base URL
  2. Run from your nsca-archive folder:
       python3 generate_thumbnails.py
  3. Commit and push everything (thumbnails/ folder + updated nsca_catalog.json)
"""

import os
import json
import subprocess

# ── SET YOUR GITHUB PAGES URL ────────────────────────────────────────────────
GITHUB_PAGES_URL = 'https://zoefried.github.io/nsca-archive'
# ────────────────────────────────────────────────────────────────────────────

DROPBOX_FOLDER  = os.path.expanduser('~/Library/CloudStorage/Dropbox/Historical_NS')
CATALOG_FILE    = 'nsca_catalog.json'
THUMBNAILS_DIR  = 'thumbnails'
THUMBNAIL_WIDTH = 400  # pixels wide


def main():
    if 'YOUR-USERNAME' in GITHUB_PAGES_URL:
        print("ERROR: Set your GitHub Pages URL at the top of the script first.")
        return

    os.makedirs(THUMBNAILS_DIR, exist_ok=True)

    with open(CATALOG_FILE, 'r') as f:
        catalog = json.load(f)

    total   = len(catalog)
    updated = 0
    skipped = 0
    failed  = []

    for i, record in enumerate(catalog):
        filename = record['path'].split('/')[-1]
        if not filename.lower().endswith('.pdf'):
            skipped += 1
            continue

        # Output thumbnail filename: same name but .jpg
        thumb_name = filename.rsplit('.', 1)[0] + '.jpg'
        thumb_path = os.path.join(THUMBNAILS_DIR, thumb_name)
        pdf_path   = os.path.join(DROPBOX_FOLDER, filename)

        print(f"[{i+1}/{total}] {filename}", end=' ... ', flush=True)

        if not os.path.exists(pdf_path):
            print("✗ PDF not found in Dropbox")
            failed.append(filename)
            continue

        if os.path.exists(thumb_path):
            print("already exists, skipping")
            skipped += 1
            # Still update previewUrl if missing
            thumb_url = f"{GITHUB_PAGES_URL}/thumbnails/{thumb_name}"
            if record.get('previewUrl') != thumb_url:
                record['previewUrl'] = thumb_url
                updated += 1
            continue

        # Use pdftoppm (from poppler) to render first page
        try:
            result = subprocess.run([
                'pdftoppm',
                '-jpeg',
                '-f', '1', '-l', '1',       # first page only
                '-scale-to-x', str(THUMBNAIL_WIDTH),
                '-scale-to-y', '-1',          # maintain aspect ratio
                pdf_path,
                os.path.join(THUMBNAILS_DIR, filename.rsplit('.', 1)[0])
            ], capture_output=True, timeout=30)

            # pdftoppm names output like: basename-1.jpg or basename-000001.jpg
            # Find whatever it generated and rename to our clean thumb_name
            prefix = filename.rsplit('.', 1)[0]
            generated = None
            for fn in sorted(os.listdir(THUMBNAILS_DIR)):
                # Match exactly: prefix + pdftoppm page suffix (-1.jpg or -000001.jpg)
                if fn.startswith(prefix) and fn.endswith('.jpg') and fn[len(prefix):len(prefix)+1] == '-':
                    generated = os.path.join(THUMBNAILS_DIR, fn)
                    break

            if generated and os.path.exists(generated):
                if generated != thumb_path:
                    os.rename(generated, thumb_path)
                thumb_url = f"{GITHUB_PAGES_URL}/thumbnails/{thumb_name}"
                record['previewUrl'] = thumb_url
                print("✓")
                updated += 1
            else:
                print("✗ thumbnail not created")
                failed.append(filename)

        except subprocess.TimeoutExpired:
            print("✗ timed out")
            failed.append(filename)
        except FileNotFoundError:
            print("\nERROR: pdftoppm not found. Run: brew install poppler")
            return

        # Save progress after each file
        with open(CATALOG_FILE, 'w') as f:
            json.dump(catalog, f, indent=2)

    # Final save
    with open(CATALOG_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)

    print(f"\nDone. {updated} thumbnails created, {skipped} skipped, {len(failed)} failed.")
    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  {f}")
    print(f"\nNext: commit and push the thumbnails/ folder and nsca_catalog.json to GitHub.")


if __name__ == '__main__':
    main()
