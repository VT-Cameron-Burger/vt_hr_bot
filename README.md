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

## Local LLM / Hosted fallback

This project can synthesize answers locally using small instruction models (via Hugging Face transformers). For higher-quality responses you can enable a hosted fallback (OpenAI) by installing the `openai` package and setting the `OPENAI_API_KEY` environment variable.

Example (macOS / zsh):

```bash
# install the optional package
pip install openai

# export your API key (keep this secret)
export OPENAI_API_KEY="sk-..."

# Optionally choose a model (default: gpt-3.5-turbo)
export OPENAI_FALLBACK_MODEL="gpt-4o-mini"
```

When enabled, the local LLM wrapper will call the OpenAI ChatCompletion API if local generation fails or if you explicitly configure it to do so.

## Rebuilding vectors and seeding PDFs

There are helper scripts in `scripts/`:

- `scripts/seed_pdfs.py` — download a few public sample PDFs into `downloaded_pdfs/` (or pass your own URLs).
- `scripts/rebuild_vectors.py` — read PDFs from `downloaded_pdfs/`, vectorize them, and write `pdf_vectors.pkl`.

Example workflow:

```bash
source .venv/bin/activate
python scripts/seed_pdfs.py
python scripts/rebuild_vectors.py --pdf-dir downloaded_pdfs --model all-mpnet-base-v2
python ui/server.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
