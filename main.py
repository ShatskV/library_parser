import os
from pathlib import Path
from urllib.parse import urljoin
import re
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


url_book_template = 'https://tululu.org/b{}/'
filename_template ='{}. {}.txt'


def download_txt(url, filename, folder='books/'):
    try:
        response = requests.get(url)
    except requests.HTTPError as e:
        print(f'HTTP error: {e}')
        return None
    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath



def check_for_redirect(response):
    if response.status_code == 302:
        raise requests.HTTPError


def parse_book_html(book_html):
    page_soup = BeautifulSoup(book_html, 'lxml')
    name_and_author = page_soup.find('div', id='content').find('h1').text
    book_href = page_soup.find('a', {'href': re.compile('/txt.php*')})
    if book_href:
        book_link = book_href.get('href')
    else:
        print('No link for this book')
        book_link = None
    name, author = name_and_author.split('::')
    author = author.strip()
    name = name.strip()
    return name, author, book_link


def fetch_books(url_template, filename_template, folder='books/', start_id=1, end_id=10):

    id_ = 1
    for i in range(start_id, end_id + 1):
        url = url_template.format(i)
        try:
            response = requests.get(url, allow_redirects=False)
        except requests.HTTPError as e:
            print(f'HTTP error: {e}')
            return
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            print(f'No book found: {url}')
        else:
            page_html = response.text
            book_name, _, book_relative_link = parse_book_html(page_html)
            if book_relative_link:
                book_link = urljoin(url, book_relative_link)
                filename = filename_template.format(id_, book_name)
                download_txt(book_link, filename, folder)
                id_ += 1


def get_page_html(url):
    try:
        response = requests.get(url, allow_redirects=False)
    except requests.HTTPError as e:
        print(f'HTTP error: {e}')
        return None
    return response.text


def main():
    fetch_books(url_book_template, filename_template)

if __name__ == '__main__':
    main()
