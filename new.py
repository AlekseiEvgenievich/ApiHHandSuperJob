import requests
import pathlib
import json
from urllib.parse import unquote
from urllib.parse import urlsplit
import os

if __name__ == '__main__':
    path = pathlib.Path("pattt")
    path.mkdir(parents=True, exist_ok=True)
    file_name = path/ "gg.json"
    url = 'https://api.hh.ru/vacancies/'
    page = 0
    pages_number = 1
    while page < pages_number:
        page_response = requests.get(url, params={'page': page,'text': 'JavaScript','search_field': 'name', 'area':1,'period':30})
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload['pages']
        page += 1
        for vacancy in page_payload["items"]:
            print(vacancy)
            print("=========")
