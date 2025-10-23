import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def create_download_directory(directory):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def is_valid_pdf_url(url):
    """Check if the URL points to a PDF file."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    return path.endswith('.pdf')

def download_pdf(url, directory):
    """Download a PDF file from the given URL."""
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

def get_pdf_links(url):
    """Extract all PDF links from a webpage."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        pdf_links = []
        # Find all links on the page
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute URLs
                full_url = urljoin(url, href)
                if is_valid_pdf_url(full_url):
                    pdf_links.append(full_url)
        
        return pdf_links
    except Exception as e:
        print(f"Error fetching webpage {url}: {str(e)}")
        return []

def main():
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