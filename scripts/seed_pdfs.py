#!/usr/bin/env python3
"""Seed the downloaded_pdfs/ directory with a few public sample PDFs.

This script downloads a short list of small, public sample PDFs and
saves them into `downloaded_pdfs/`. You can also pass additional URLs
on the command line.

Usage:
  python scripts/seed_pdfs.py [url1 url2 ...]

If no URLs are provided, a small curated list of public sample PDFs is
used (non-exhaustive). The script is conservative and will skip files
that fail to download.
"""
import argparse
import os
import sys

# Ensure repo root is on sys.path so imports from repo work when running this
# script from scripts/ directly.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pdf_downloader import create_download_directory, download_pdf

DEFAULT_URLS = [
    # Small public sample PDFs
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    "https://www.africau.edu/images/default/sample.pdf",
]


def main():
    parser = argparse.ArgumentParser(description='Seed downloaded_pdfs with sample PDFs')
    parser.add_argument('urls', nargs='*', help='Optional list of PDF URLs to download')
    parser.add_argument('--out-dir', default='downloaded_pdfs', help='Directory to save PDFs')
    args = parser.parse_args()

    urls = args.urls if args.urls else DEFAULT_URLS

    create_download_directory(args.out_dir)

    success = 0
    for url in urls:
        print(f"Downloading {url}...")
        if download_pdf(url, args.out_dir):
            success += 1

    print(f"Downloaded {success}/{len(urls)} PDFs to {args.out_dir}")


if __name__ == '__main__':
    main()
