import argparse
import json
import time
from urllib.parse import urljoin
from itertools import count
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path

from books_logger import logger
from tululu import download_image, download_txt, parse_book_page


def get_book_urls_from_page(main_page_url, page_html):
    page_soup = BeautifulSoup(page_html, 'lxml')
    selector = ".bookimage a"
    book_urls = []
    book_blocks = page_soup.select(selector)
    for block in book_blocks:
        book_url = urljoin(main_page_url, block.get('href'))
        book_urls.append(book_url)
    return book_urls


def parse_args_from_terminal():
    parser = argparse.ArgumentParser(
                    description='Задайте диапазон страниц для скачивания книг:')
    parser.add_argument('-s', '--start_page', help="Начальная страница", type=int, default=1)
    parser.add_argument('-e', '--end_page', help="Конечная страница", type=int)
    parser.add_argument('-df', '--dest_folder', help="Путь каталога для сохранения книг", default='')
    parser.add_argument('-si', '--skip_imgs', help="Не загружать обложки книг", action='store_true')
    parser.add_argument('-st', '--skip_txt', help="Не загружать тексты книг", action='store_true')
    parser.add_argument('-jp', '--json_path', help="Путь файла json для сохранения данных о книгах", default='books.json')

    args = parser.parse_args()

    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_path = args.json_path
    start_page = args.start_page
    end_page = args.end_page

    return {'start_page': start_page,
            'end_page': end_page,
            'dest_folder': dest_folder,
            'skip_imgs': skip_imgs,
            'skip_txt': skip_txt,
            'json_path': json_path,
            }

def fetch_fantastic_books(start_page=1, end_page=None, dest_folder='', json_path='books.json',
                          skip_imgs=False, skip_txt=False):
    url_template = 'https://tululu.org/l55/{}'
    
    books_folder = 'books'
    images_folder = 'images'
    image_filename_template = '{}.jpg'
    book_filename_template = '{}.txt'
    books_folder = os.path.join(dest_folder, books_folder)
    images_folder = os.path.join(dest_folder, images_folder)
    book_urls = []
    for num_page in count(start_page):
        if num_page == end_page:
            break
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
            book_path = download_txt(book_link, book_filename, books_folder) if not skip_txt else None
            img_path = download_image(image_link, image_filename, images_folder) if not skip_imgs else None
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

    if json_path.count(os.sep) == 0:
        json_path = os.path.join(dest_folder, json_path)
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(books, file, indent=4, ensure_ascii=False)
            

def main():
    terminal_args = parse_args_from_terminal()
    fetch_fantastic_books(**terminal_args)


if __name__ == '__main__':
    main()
