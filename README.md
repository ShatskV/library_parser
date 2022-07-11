<<<<<<< HEAD
# Скачивание книг с сайта [tululu.org](https://tululu.org/) и их автоверстка
=======
# Скачивание и книг с сайта [tululu.org](https://tululu.org/) и их автоверстка
>>>>>>> main

Программа умеет: 
- Скачивать книги заданного диапазона страниц из раздела "Фантастика" с сайта путем парсинга страниц
- Верстать скачанные книги в автоматическом режиме

### Как установить

- Python3 должен быть установлен
- Затем используйте `pip` (или `pip3`, еслить есть конфликт с Python2) для установки зависимостей: 
    ```
    pip install -r requirements.txt
    ```

- Рекомендуется использовать [virtualenv/venv](https://docs.python.org/3/library/venv.html) для изоляции проекта.


### Как пользоваться
## Программа парсинга запускается через терминал:

```
   python3 parse_tululu_category.py
```
- Книги будут загружены в папку **books**, обложки к ним в - **images** и данные о книгах в файл **books.py** в корень проекта. Книги будут с 1-ой страницы по последнюю в разделе (значения по-умолчанию)

- Можно указать следующие аргументы в терминале:
    - Начальная страница раздела
    - Конечная страница раздела
    - Путь каталога для сохранения книг
    - Выключение загрузки обложек
    - Выключение загрузки текстов книг
    - Путь файла json для сохранения данных о книгах

    ```
    $ python3 parse_tululu_category.py -h
    usage: parse_tululu_category.py [-h] [-s START_PAGE] [-e END_PAGE] [-df DEST_FOLDER] [-si] [-st] [-jp JSON_PATH]

    Задайте диапазон страниц для скачивания книг:

    optional arguments:
    -h, --help            show this help message and exit
    -s START_PAGE, --start_page START_PAGE
                            Начальная страница
    -e END_PAGE, --end_page END_PAGE
                            Конечная страница
    -df DEST_FOLDER, --dest_folder DEST_FOLDER
                            Путь каталога для сохранения книг
    -si, --skip_imgs      Не загружать обложки книг
    -st, --skip_txt       Не загружать тексты книг
    -jp JSON_PATH, --json_path JSON_PATH
                        Путь файла json для сохранения данных о книгах
    ```
    
    ``` 
    python3 tululu.py -s 600 -e 620
    ```

- Скрипт записывает в лог ошибки при выполнении, файл **tululu.log**

## Программа автоверстки скачанных книг запускается через терминал:

```
   python3 render_website.py
```

- Можно указать количество книг на странице в терминале:
```
    $ python3 render_website.py -h
    usage: render_website.py [-h] [-b BOOKS]

    Задайте количество книг на странице:

    optional arguments:
      -h, --help            show this help message and exit
      -b BOOKS, --books BOOKS
                            Количество книг на страницу default - 10 
```
<<<<<<< HEAD
- Адрес сайта - [books library](https://shatskv.github.io/library_parser/pages/index1.html) 
=======
- Адрес сайта - [books library](https://shatskv.github.io/library_parser/pages/index4.html) 
>>>>>>> main

### Цель проекта

Код написан в образовательный целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).

