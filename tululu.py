import argparse
import logging
import os
import re
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

logger = logging.getLogger('main')
logger.setLevel(logging.ERROR)
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
log_handler = RotatingFileHandler('tululu.log', maxBytes=1024*1024, backupCount=2)
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

def download_txt(url, filename, folder='books/'):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.ConnectionError:
        raise
    except requests.HTTPError:
        raise
    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_image(url, filename, folder='images/'):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.ConnectionError:
        raise
    except requests.HTTPError:
        raise
    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def check_for_redirect(response):
    if response.status_code == 302:
        raise requests.HTTPError('code: 404, No book fot this url')


def parse_args_from_terminal():
    parser = argparse.ArgumentParser(
    description='Задайте диапазон скачивания книг:'
                )
    parser.add_argument('-s', '--book_start_id', help="Начальный ID книги", type=int, default=1)
    parser.add_argument('-e', '--book_end_id', help="Конечный ID книги", type=int, default=10)
    args = parser.parse_args()
    book_start_id = args.book_start_id
    book_end_id = args.book_end_id
    return book_start_id, book_end_id


def parse_book_page(book_html):
    page_soup = BeautifulSoup(book_html, 'lxml')
    name_and_author = page_soup.find('div', id='content').find('h1').text

    book_href = page_soup.find('a', {'href': re.compile('/txt.php*')})
    image_route = page_soup.find('div', class_='bookimage').find('img').get('src')

    genres_hrefs = page_soup.find('span', class_='d_book').find_all('a', href=True)
    genres = [genre_href.text for genre_href in genres_hrefs]

    comments_class_texts = page_soup.find_all('div', 'texts')
    comments = [comment.find('span', class_ ='black').text for comment in comments_class_texts]
    
    book_route = book_href.get('href') if book_href else None
    
    name, author = name_and_author.split('::')
    author = author.strip()
    name = name.strip()
    return {'name': name,
            'author': author, 
            'book_route': book_route,
            'image_route': image_route, 
            'comments': comments,
            'genres': genres}


def fetch_books(book_start_id=1, book_end_id=10):
    url_book_template = 'https://tululu.org/b{}/'
    book_filename_template ='{}. {}.txt'
    books_folder='books/'
    images_folder='images/'
    image_filename_template='{}.jpg'
    book_id_in_local_lib = 1

    for book_id in range(book_start_id, book_end_id + 1):
        url = url_book_template.format(book_id)
        try:
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
            check_for_redirect(response)
        except requests.ConnectionError as e:
            logger.error(f'url: {url} Connection error: {e}')
            print(f'url: {url}\n Connection error: {e}\n', file=sys.stderr)
            time.sleep(5)
        except requests.HTTPError as e:
             logger.error(f'HTTP error: {e}')
             print(f'url: {url}\n HTTP error: {e}\n', file=sys.stderr)
        else:
            page_html = response.text
            book_parsed = parse_book_page(page_html)
            if book_parsed.get('book_route'):
                book_link = urljoin(url, book_parsed['book_route'])
                image_link = urljoin(url, book_parsed['image_route'])

                book_filename = book_filename_template.format(book_id_in_local_lib, book_parsed['name'])
                image_filename = image_filename_template.format(book_id_in_local_lib)
                try:
                    download_txt(book_link, book_filename, books_folder)
                    download_image(image_link, image_filename, images_folder)
                except requests.ConnectionError as e:
                    logger.error(f'Connection error: {e}')
                    print(f'Connection error while download book files: {e}\n', file=sys.stderr)
                    time.sleep(5)
                except requests.HTTPError as e:
                    logger.error(f'HTTP error while download book files: {e}')
                    print(f'url: {url}\n Connection error: {e}\n', file=sys.stderr)
                book_id_in_local_lib += 1


def main():
    book_start_id, book_end_id = parse_args_from_terminal()
    fetch_books(book_start_id=book_start_id, book_end_id=book_end_id)


if __name__ == '__main__':
    main()