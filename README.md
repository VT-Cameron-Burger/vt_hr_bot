# VT HR Bot

A Python script that downloads PDF files from a specified website.

## Features

- Scans websites for PDF links
- Downloads PDFs to a local directory
- Handles both relative and absolute URLs
- Includes error handling and progress reporting
- Verifies PDF content type

## Requirements

- Python 3.x
- requests
- beautifulsoup4

## Installation

1. Clone the repository:
```bash
git clone https://github.com/VT-Cameron-Burger/vt_hr_bot.git
cd vt_hr_bot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install requests beautifulsoup4
```

## Usage

Run the script:
```bash
python pdf_downloader.py
```

The script will:
1. Prompt for a target website URL
2. Create a "downloaded_pdfs" directory
3. Scan the website for PDF links
4. Download all found PDFs
5. Show a summary of successful downloads

## Note

Make sure you have permission to download files from the target website. Some websites may have restrictions on automated downloads.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
