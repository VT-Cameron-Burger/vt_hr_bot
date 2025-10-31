#!/usr/bin/env python3
"""Rebuild the vector store from PDFs in `downloaded_pdfs/`.

Usage:
  python scripts/rebuild_vectors.py --pdf-dir downloaded_pdfs --model all-mpnet-base-v2

This wraps the existing `load_data.create_new_vectors` flow.
"""
import argparse
from load_data import create_new_vectors


def main():
    parser = argparse.ArgumentParser(description='Rebuild pdf_vectors.pkl from PDFs')
    parser.add_argument('--pdf-dir', default='downloaded_pdfs', help='Directory containing PDFs')
    parser.add_argument('--model', default='all-mpnet-base-v2', help='Embedding model to use')
    parser.add_argument('--out', default='pdf_vectors.pkl', help='Output vector file')
    args = parser.parse_args()

    system = create_new_vectors(pdf_directory=args.pdf_dir, model_name=args.model, vector_file=args.out)
    if system:
        print(f"Saved vectors to {args.out}")
    else:
        print("No vectors created. Check logs for details.")


if __name__ == '__main__':
    main()
