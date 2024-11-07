
# Books Downloader 


This Python script allows you to download books from AnyFlip and FlipHTML5. It retrieves book pages and saves them in a specified format, providing a convenient way to access content offline.

## Features

- Downloads books from AnyFlip and FlipHTML5.
- Saves downloaded content as images or PDFs.
- Progress tracking for download and PDF creation with rich for a clean display.


## Prerequisites

- Python 3.6+
- The script uses the following Python modules:
    - BeautifulSoup (from bs4): To parse HTML content and extract relevant data.
    - requests - for making HTTP requests.
    - Pillow - for handling images.
    - rich - for creating progress bars.
    - reportlab - for creating PDFs.
    
## Installation

To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```
## Setup

1. Clone the repository:

```bash
git clone https://github.com/prak4sh/books-downloader.git

```

2. Navigate to the project directory:

```bash
cd book-downloader
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```


## Usage/Examples

To download a book, specify the URL of the book on AnyFlip or FlipHTML5. The script will retrieve each page and save it to a specified folder, optionally creating a PDF.

```python
python download_books.py <url> --temp-download-folder <folder_name> --title <pdf_title> --keep-download-folder
```

Replace <url> with the book's URL, <folder_name> with the name of the folder where you want the files saved, and <pdf_title> with the title for the generated PDF document.
Arguments

- url (required): The URL of the AnyFlip or FlipHTML5 book.
- --temp-download-folder (optional): Specifies a temporary folder for downloading images.
- --title (optional): Sets the title of the generated PDF document.
- --keep-download-folder (optional): If specified, retains the temporary download folder after completion.

## Troubleshooting

If you encounter issues, ensure that:

    - The book URL is accessible and publicly available.
    - Your internet connection is active.
    - The output directory has write permissions.
## Contributing

Feel free to open an issue or submit a pull request if you find a bug or have suggestions for improvement.

# Inspired by:
    https://github.com/Lofter1/anyflip-downloader

