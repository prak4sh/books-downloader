import requests
from urllib.parse import urlparse, urljoin
from rich import print
from bs4 import BeautifulSoup
import re
import json
import os
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from PIL import Image
from reportlab.pdfgen import canvas
import argparse
from datetime import datetime


class DownloadBooks:
    def __init__(self):
        self.url = ''
        self.title = ''
        self.page_count = 0
        self.page_urls = []

    def get_soup(self, response):
        return BeautifulSoup(response.text, 'html.parser')

    def time_now(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M')

    def get_response(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': self.url,
        }
        response = requests.get(url, headers=headers)
        return response
    
    def print_info(self, msg, sw='INF'):
        if sw == 'INF':
            print(f'[green]{self.time_now()} [INF][/green] {msg}')
        elif sw == 'ERR':
            print(f'[red]{self.time_now()} [ERR] {msg}[/red]')


    def find_iframe(self):
        response = self.get_response(self.url)
        soup = self.get_soup(response)
        iframe_divs = soup.find_all('iframe')
        for iframe_div in iframe_divs:
            found_url = iframe_div.get('src')
            if self.supported_url(found_url):
                self.url = found_url
        pass

    def supported_url(self, url):
        if 'fliphtml5.com' in url or 'anyflip.com' in url:
            return True
        else:
            return False

    def download_config_js(self):
        if not self.supported_url(self.url):
            self.find_iframe()
        parse_url = urlparse(self.url)
        domain = parse_url.netloc
        url_path = parse_url.path
        if 'anyflip.com' in domain:
            full_url = urljoin("https://online.anyflip.com/", f"{url_path.replace('/mobile/index.html','')}")
            config_js_url = urljoin(full_url, 'mobile/javascript/config.js')
        elif 'fliphtml5.com' in domain:
            full_url = urljoin("https://online.fliphtml5.com/", url_path)
            config_js_url = urljoin(full_url, 'javascript/config.js')
        else:
            return None
        response = self.get_response(config_js_url)
        return response.text
    
    def get_book_title(self, config_js):
        match = re.search(r'"title"\s*:\s*"([^"]*)"', config_js)
        return match.group(1) if match else None

    def get_book_count(self, config_js):
        match = re.search(r'"pageCount"\s*:\s*(\d+)', config_js)
        return int(match.group(1)) if match else 0
    
    def get_page_file_names(self, config_js):
        results = []

        try:
            # Extract the fliphtml5_pages array from the config data
            json_string = re.sub(r'^var\s+htmlConfig\s*=\s*', '', config_js.strip())
            json_string = re.sub(r';$', '', json_string.strip())
            parsed_json = json.loads(json_string)
            fliphtml5_pages = parsed_json['fliphtml5_pages']

            for fliphtml5_page in fliphtml5_pages:
                results.append(fliphtml5_page['n'][0])
        except: 
            pass
        return results

    def prepare_download(self):
        config_js = self.download_config_js()
        if config_js:
            self.page_count = self.get_book_count(config_js)
            self.title = self.get_book_title(config_js)
            self.print_info(f'Book Found: {self.title}, Total Pages: {self.page_count}')

            page_file_names = self.get_page_file_names(config_js)
            if page_file_names:
                image_urls = [urljoin(self.url, f"files/large/{x}") for x in page_file_names]
            else:
                image_urls = [urljoin(self.url, f"files/large/{i}.jpg")
                                for i in range(1, self.page_count + 1)]
            return image_urls
        else:
            self.print_info(f'Book Not Found', 'ERR')
            return []

    def download_images(self, page_urls, download_folder):
        os.makedirs(download_folder, exist_ok=True)
        
        # Customize the progress display
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),  # Shows progress as a percentage
            TextColumn("[bold yellow]{task.completed}/{task.total} "),
            TimeRemainingColumn(),  # Shows estimated time remaining
        ) as progress:
            
            # Add the download task with the total number of URLs
            task = progress.add_task("Downloading images", total=len(page_urls))
            
            for i, url in enumerate(page_urls):
                extension = os.path.splitext(url)[1]
                filename = f"{i:04d}{extension}"
                filename_with_path = os.path.join(download_folder, filename)
                response = self.get_response(url)
                with open(filename_with_path,  'wb') as f:
                    f.write(response.content)
                
                # Update the progress bar
                progress.update(task, advance=1)

                
    def create_pdf(image_files, image_dir, pdf):
        # Customize the progress display
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),  # Shows progress as a percentage
            TextColumn("[bold yellow]{task.completed}/{task.total}"),
            TimeRemainingColumn(),  # Shows estimated time remaining
        ) as progress:
            
            # Add a progress task with the total number of images
            task = progress.add_task("Creating PDF", total=len(image_files))
            
            for image_file in image_files:
                img = Image.open(os.path.join(image_dir, image_file))
                pdf.setPageSize(img.size)
                pdf.drawImage(os.path.join(image_dir, image_file), 0, 0)
                pdf.showPage()
                
                # Update the progress bar
                progress.update(task, advance=1)

        pdf.save()

    def main(self):
        parser = argparse.ArgumentParser(description="Download and convert AnyFlip or FLIPHTML5 books to PDF")
        parser.add_argument("url", help="URL of the AnyFlip or FlipHtml5 book")
        parser.add_argument("--temp-download-folder", help="Temporary download folder name")
        parser.add_argument("--title", help="Title of the generated PDF document")
        parser.add_argument("--keep-download-folder", action="store_true", help="Keep the temporary download folder")
        args = parser.parse_args()

        self.url = args.url
        pages_url = self.prepare_download()

        temp_download_folder = args.temp_download_folder or self.title
        output_file = f"{args.title or self.title}.pdf"

        self.download_images(pages_url, temp_download_folder)
        self.print_info("Converting to PDF", 'INF')
        try:
            self.create_pdf(output_file, temp_download_folder)
            self.print_info(f"Task completed successfully. Output is saved as {output_file}", 'INF')
        except Exception as e:
            self.print_info(f'Error in creating pdf. Error: {e}', 'ERR')
        
        if not args.keep_download_folder:
            import shutil
            shutil.rmtree(temp_download_folder)


if __name__=="__main__":
    db = DownloadBooks()
    db.main()