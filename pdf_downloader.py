from typing import List, Optional
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def create_download_directory(directory: str) -> None:
    """Create a directory if it doesn't exist.
    
    Args:
        directory: Path to the directory to create.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def is_valid_pdf_url(url: str) -> bool:
    """Check if the URL points to a PDF file.
    
    Args:
        url: The URL to check.
        
    Returns:
        bool: True if the URL ends with .pdf, False otherwise.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()
    return path.endswith('.pdf')

def download_pdf(url: str, directory: str) -> bool:
    """Download a PDF file from the given URL.
    
    Args:
        url: The URL of the PDF to download.
        directory: The directory to save the PDF in.
        
    Returns:
        bool: True if download was successful, False otherwise.
    """
    try:
        # Get the filename from the URL
        filename = os.path.join(directory, os.path.basename(urlparse(url).path))
        
        # Make the request with a timeout
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Check if the content type is PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' not in content_type:
            print(f"Warning: {url} might not be a PDF file.")
        
        # Save the file
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Successfully downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def get_pdf_links(url: str) -> List[str]:
    """Extract all PDF links from a webpage.
    
    Args:
        url: The URL of the webpage to scan for PDF links.
        
    Returns:
        List[str]: A list of URLs to PDF files found on the page.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        pdf_links: List[str] = []
        # Find all links on the page
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and isinstance(href, (str, list)):  # href can be str or list of str
                # Convert to string if it's a list
                href_str = href[0] if isinstance(href, list) else href
                # Convert relative URLs to absolute URLs
                full_url = urljoin(url, str(href_str))  # Ensure we pass a string
                if is_valid_pdf_url(full_url):
                    pdf_links.append(full_url)
        
        return pdf_links
    except Exception as e:
        print(f"Error fetching webpage {url}: {str(e)}")
        return []

def main() -> None:
    """Main function to run the PDF downloader."""
    # Get the target website URL from user input
    target_url = input("Enter the target website URL: ")
    
    # Create a directory to store the PDFs
    download_dir = "downloaded_pdfs"
    create_download_directory(download_dir)
    
    # Get all PDF links from the website
    print(f"Scanning {target_url} for PDF files...")
    pdf_links = get_pdf_links(target_url)
    
    if not pdf_links:
        print("No PDF files found on the webpage.")
        return
    
    print(f"Found {len(pdf_links)} PDF files.")
    
    # Download each PDF
    successful_downloads = 0
    for url in pdf_links:
        if download_pdf(url, download_dir):
            successful_downloads += 1
    
    print(f"\nDownload complete! Successfully downloaded {successful_downloads} out of {len(pdf_links)} PDFs.")
    print(f"PDFs are stored in the '{download_dir}' directory.")

if __name__ == "__main__":
    main()