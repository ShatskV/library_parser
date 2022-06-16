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


def download_image(url, filename, folder='images/'):
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


def parse_book_page(book_html):
    page_soup = BeautifulSoup(book_html, 'lxml')
    name_and_author = page_soup.find('div', id='content').find('h1').text

    book_href = page_soup.find('a', {'href': re.compile('/txt.php*')})
    image_route = page_soup.find('div', class_='bookimage').find('img').get('src')

    genres_hrefs = page_soup.find('span', class_='d_book').find_all('a', href=True)
    genres = [genre_href.text for genre_href in genres_hrefs]

    comments = []
    comments_class_texts = page_soup.find_all('div', 'texts')
    if comments_class_texts:
        comments = [comment.find('span', class_ ='black').text for comment in comments_class_texts]
    if book_href:
        book_route = book_href.get('href')
    else:
        print('No link for this book')
        book_route = None
    
    name, author = name_and_author.split('::')
    author = author.strip()
    name = name.strip()
    return {'name': name,
            'author': author, 
            'book_route': book_route,
            'image_route': image_route, 
            'comments': comments,
            'genres': genres}


def fetch_books(url_template, book_filename_template='{}. {}.txt', image_filename_template='{}.jpg', 
                books_folder='books/', images_folder='images/', start_id=1, end_id=10):
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
            book_parsed = parse_book_page(page_html)
            book_parsed['comments'] = None
            if book_parsed.get('book_route'):
                book_link = urljoin(url, book_parsed['book_route'])
                image_link = urljoin(url, book_parsed['image_route'])

                book_filename = book_filename_template.format(id_, book_parsed['book_name'])
                image_filename = image_filename_template.format(id_)

                download_txt(book_link, book_filename, books_folder)
                download_image(image_link, image_filename, images_folder)

                id_ += 1


def get_page_html(url):
    try:
        response = requests.get(url, allow_redirects=False)
    except requests.HTTPError as e:
        print(f'HTTP error: {e}')
        return None
    return response.text


def main():
    fetch_books(url_book_template)

if __name__ == '__main__':
    main()
