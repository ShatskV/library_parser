import requests
from books_logger import logger
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tululu import download_image, parse_book_page, download_txt
import json


def get_book_urls_from_page(main_page_url, page_html):
    page_soup = BeautifulSoup(page_html, 'lxml')
    book_classes = page_soup.find_all('div', class_='bookimage')
    book_urls = []
    for book_class in book_classes:
        book_route = book_class.find('a').get('href')
        book_url = urljoin(main_page_url, book_route)
        book_urls.append(book_url)
    return book_urls


def fetch_fantastic_books(num_pages=10):
    url_template = 'https://tululu.org/l55/{}'
    book_filename_template ='{}.txt'
    books_folder='books/'
    images_folder='images/'
    image_filename_template='{}.jpg'
    book_urls = []
    for num_page in range(1, num_pages + 1):
        try:
            url = url_template.format(num_page)
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
        except requests.ConnectionError as e:
            logger.error(f'url: {url} Connection error: {e}')
            time.sleep(5)
            continue
        except requests.HTTPError as e:
            logger.error(f'url: {url} HTTP error: {e}')
            continue
        if response.status_code == 302:
                logger.error('code: 404, No more pages found')
                return
        page_book_urls = get_book_urls_from_page(url, response.text)
        book_urls += page_book_urls

    books = []
    for book_url in book_urls:
        try:
            response = requests.get(book_url, allow_redirects=False)
            response.raise_for_status()
        except requests.ConnectionError as e:
            logger.error(f'url: {url} Connection error: {e}')
            time.sleep(5)
            continue
        except requests.HTTPError as e:
            logger.error(f'url: {url} HTTP error: {e}')
            continue

        page_html = response.text
        book_parsed = parse_book_page(page_html)

        if not book_parsed.get('book_route'):
            logger.error(f'No book text for this url: {book_url}')
            continue
        _, book_id = book_url.split('/b')
        book_id = book_id.strip('/')

        book_link = urljoin(url, book_parsed['book_route'])
        image_link = urljoin(url, book_parsed['image_route'])

        book_filename = book_filename_template.format(book_parsed['name'])
        image_filename = image_filename_template.format(book_id)
        try:
            book_path = download_txt(book_link, book_filename, books_folder)
            img_path = download_image(image_link, image_filename, images_folder)
        except requests.ConnectionError as e:
            logger.error(f'Connection error while download book files: {e}')
            time.sleep(5)
            continue
        except requests.HTTPError as e:
            logger.error(f'HTTP error while download book files: {e}')
            continue
        book = {
            'title': book_parsed['name'],
            'author': book_parsed['author'],
            'img_src': img_path,
            'book_path': book_path, 
            'comments': book_parsed['comments'],
            'genres': book_parsed['genres']
        }
        books.append(book)
    with open('books.json', 'w', encoding='utf-8') as file:
        json.dump(books, file, indent=4, ensure_ascii=False)
            

def main():
    fetch_fantastic_books(4)


if __name__ == '__main__':
    main()
