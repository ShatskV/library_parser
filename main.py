import requests
from pathlib import Path

url_tepmplate = 'https://tululu.org/txt.php?id=3216{}'
filepath_template ='books/id{}.txt'

def get_books(url, filepath_template):
    response = requests.get(url)
    content = response.content

    directory = Path(filepath_template).parent
    Path(directory).mkdir(parents=True, exist_ok=True)
    for i in range(10):

        try:
            response = requests.get(url.format(i))
        except requests.HTTPError as e:
            print('HTTP error: {e}')
            return
        content = response.content
        filepath = filepath_template.format(i+1)
        with open(filepath, 'wb') as file:
                file.write(content)

def main():
    get_books(url_tepmplate, filepath_template)

if __name__ == '__main__':
    main()