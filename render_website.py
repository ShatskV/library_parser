import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

with open('books.json', 'r') as file:
    books = json.load(file)

books_chunked = list(chunked(books, 2))
def on_reload():
    rendered_page = template.render(books=books_chunked)
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print("Site rebuild")


on_reload()

server = Server()

server.watch('template.html', on_reload)

server.serve(root='.')
