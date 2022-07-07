import json
import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

BOOKS_PER_PAGE = 10


def render_pages(template, books, folder='pages', num_books_per_page=10):
    if os.path.exists(folder) and os.path.isdir(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)
    books_per_pages = list(chunked(books, num_books_per_page))
    filename_template = 'index{}.html'
    for num, books_per_page in enumerate(books_per_pages, start=1):
        books_chunked = list(chunked(books_per_page, 2))
        filepath = os.path.join(folder, filename_template.format(num))
        rendered_page = template.render(books=books_chunked, 
                                        num_pages=len(books_per_pages),
                                        current_page=num)
        with open(filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)

        
def on_reload():
    env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html', 'xml'])
            )
    template = env.get_template('template.html')
    with open('books.json', 'r') as file:
        books = json.load(file)
    render_pages(template, books)
    print("Site rebuild")


def main():
    on_reload()

    server = Server()

    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == "__main__":
    main()
