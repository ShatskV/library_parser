import argparse
import json
import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

BOOKS_PER_PAGE = 10


def parse_args_from_terminal():
    parser = argparse.ArgumentParser(
                    description='Задайте количество книг на странице:')
    parser.add_argument('-b', '--books', help="Количество книг на страницу default - 10", type=int, default=10)
    args = parser.parse_args()
    return args.books


def on_reload():
    render_pages(books, books_per_page)
    print("Site rebuild")


def render_pages(books, folder='pages', books_per_page=10):
    env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html', 'xml'])
            )
    template = env.get_template('template.html')
    if os.path.exists(folder) and os.path.isdir(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)
    books_per_pages = list(chunked(books, books_per_page))
    filename_template = 'index{}.html'
    for num, books_per_page in enumerate(books_per_pages, start=1):
        books_chunked = list(chunked(books_per_page, 2))
        filepath = os.path.join(folder, filename_template.format(num))
        rendered_page = template.render(books=books_chunked, 
                                        num_pages=len(books_per_pages),
                                        current_page=num)
        with open(filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == "__main__":
    books_per_page = parse_args_from_terminal()
    with open('books.json', 'r') as file:
        books = json.load(file)
    render_pages(books=books, books_per_page=books_per_page)
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
